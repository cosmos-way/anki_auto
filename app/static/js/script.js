document.addEventListener('DOMContentLoaded', function() {
    const socket = io();
    const loader = document.getElementById('loader');

    function showLoader() {
        loader.classList.remove('d-none');
    }

    function hideLoader() {
        loader.classList.add('d-none');
    }

    function resetLoader(){
        const loadingIndicator = document.getElementById('loading');
        const bar = document.getElementById('bar');
        const resultDiv = document.getElementById('data');

        loadingIndicator.style.display = 'block';
        bar.style.width = '0%';
        resultDiv.innerHTML = '';
    }

    function showErrorAndRedirect(message) {
        document.getElementById('data').innerHTML = `<pre><code class="language-json">${message}</code></pre>`;
        Prism.highlightAll();
        // setTimeout(function() {
        //     window.location.href = '/login';
        // }, 3000);
    }

    function fetchAndDisplay(url, options = {}) {
        showLoader();
        fetch(url, options)
            .then(response => response.json())
            .then(data => {
                hideLoader();
                if (data.error) {
                    console.error('Error:', data.error);
                    showErrorAndRedirect(data.error);
                } else {
                    const jsonString = JSON.stringify(data, null, 2);
                    document.getElementById('data').innerHTML = `<pre><code class="language-json">${jsonString}</code></pre>`;
                    Prism.highlightAll();
                }
            })
            .catch(error => {
                hideLoader();
                console.error('Error:', error);
                showErrorAndRedirect('An error occurred. Redirecting to login...');
            });
    }

    function fetchAndDisplayHtml(url, options = {}) {
        showLoader();
        fetch(url, options)
            .then(response => response.json())
            .then(data => {
                hideLoader();
                if (data.error) {
                    console.error('Error:', data.error);
                    showErrorAndRedirect(data.error);
                } else {
                    // const jsonString = JSON.stringify(data, null, 2);
                    document.getElementById('data').innerHTML = data['html'];
                    Prism.highlightAll();
                }
            })
            .catch(error => {
                hideLoader();
                console.error('Error:', error);
                showErrorAndRedirect('An error occurred. Redirecting to login...');
            });
    }
    function longFetchAndDisplay(url, options = {}) {
        resetLoader();
        socket.on('progress', (data) => {
            const loadingIndicator = document.getElementById('loading');
            const bar = document.getElementById('bar');
            const resultDiv = document.getElementById('data');
            bar.style.width = `${data.progress}%`;
            if (data.progress === 100) {
                loadingIndicator.style.display = 'none';
                resultDiv.innerHTML = 'Task completed!';
            }
        });
        fetch(url, options)
            .then(response => response.json())
            .then(data => {
                
                if (data.error) {
                    console.error('Error:', data.error);
                    showErrorAndRedirect(data.error);
                } else {
                    const jsonString = JSON.stringify(data, null, 2);
                    document.getElementById('data').innerHTML = `<pre><code class="language-json">${jsonString}</code></pre>`;
                    Prism.highlightAll();
                }
            })
            .catch(error => {
                hideLoader();
                console.error('Error:', error);
                showErrorAndRedirect('An error occurred. Redirecting to login...');
            });
    }

    // document.getElementById('fetchDataButton').onclick = function() {
    //     fetchAndDisplay('/notion/fetch_data', { method: 'POST', headers: { 'Content-Type': 'application/json' } });
    // };

    document.getElementById('fetchRowsButton').onclick = function() {
        const databaseId = prompt('Enter Database ID:', '6f351f4a-bc98-42b5-b605-f4d527b18df4');
        fetchAndDisplay('/notion/fetch_rows', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ database_id: databaseId })
        });
    };

    document.getElementById('fetchPageButton').onclick = function() {
        const pageId = prompt('Enter Page ID:');
        fetchAndDisplay('/notion/fetch_page', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ page_id: pageId })
        });
    };

    document.getElementById('fetchBlockChildrenButton').onclick = function() {
        const blockId = prompt('Enter Block ID:', 'default-block-id');
        fetchAndDisplay('/notion/fetch_block_children', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ block_id: blockId })
        });
    };

    document.getElementById('fetchBlockButton').onclick = function() {
        const blockId = prompt('Enter Block ID:', 'default-block-id');
        fetchAndDisplay('/notion/fetch_block', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ block_id: blockId })
        });
    };

    document.getElementById('convertPageButton').onclick = function() {
        const pageId = prompt('Enter Page ID to convert to Markdown:');
        fetchAndDisplayHtml('/notion/convert_page', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ page_id: pageId })
        });
    };

    document.getElementById('fetch_all_database_pages').onclick = function() {
        const database_id = prompt('Enter database_id to convert to Markdown:');
        longFetchAndDisplay('/notion/fetch_all_database_pages', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ database_id: database_id })
        });
    };
    document.getElementById('getAnkiButton').onclick = function() {
        const database_id = prompt('Enter database_id to convert to Markdown:');
        longFetchAndDisplay('/notion/getAnki', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ database_id: database_id })
        });
    };
});


function startLongTask() {
    
}

