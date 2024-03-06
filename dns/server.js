const express = require('express');
const app = express();
const cors = require('cors');

const port = 3002;

app.use(cors({
    origin: 'http://localhost:3000'
}));

app.get('/getServer', (req, res) => {
    res.json({ code: 200, server: `http://localhost:3001`})
});

app.listen(port, () => {
    console.log(`DNS registry running on port ${port}`);
});
