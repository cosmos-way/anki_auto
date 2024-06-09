const express = require('express');
const { Client } = require('@notionhq/client');
const { NotionToMarkdown } = require('notion-to-md');
const app = express();
const port = 3000;

app.use(express.json());

const getPageProperties = (page) => {
    const properties = page.properties;
    const question = properties['Вопрос']?.title?.[0]?.text?.content || 'No question';
    const answer = properties['Ответ']?.rich_text?.[0]?.text?.content || 'No answer';
    
    return { question, answer };
  };


app.post('/convert', async (req, res) => {
    try {
        const notion = new Client({ auth: req.body.token });
        const n2m = new NotionToMarkdown({ notionClient: notion });
        const pageId = req.body.pageId;
        
        const mdBlocks = await n2m.pageToMarkdown(pageId);
        const page = await notion.pages.retrieve({ page_id: pageId });


        const mdString = n2m.toMarkdownString(mdBlocks);
        const pageProperties = getPageProperties(page);
        res.send({pageHtml: mdString["parent"], question: pageProperties.question, answer : pageProperties.answer});
    } catch (error) {
        res.status(500).send({ error: error.message });
    }
});

app.listen(port, () => {
    console.log(`Server is running on http://localhost:${port}`);
});
