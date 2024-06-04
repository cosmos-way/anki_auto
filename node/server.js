const express = require('express');
const { Client } = require('@notionhq/client');
const { NotionToMarkdown } = require('notion-to-md');
const app = express();
const port = 3000;

app.use(express.json());

app.post('/convert', async (req, res) => {
    
    
    try {
        const notion = new Client({ auth: req.body.token });
        const n2m = new NotionToMarkdown({ notionClient: notion });

        const pageId = req.body.pageId;
        const mdBlocks = await n2m.pageToMarkdown(pageId);
        const mdString = n2m.toMarkdownString(mdBlocks);
        res.send(mdString["parent"]);
    } catch (error) {
        res.status(500).send({ error: error.message });
    }
});

app.listen(port, () => {
    console.log(`Server is running on http://localhost:${port}`);
});
