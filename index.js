const exprees = require('express')
const app = exprees()

app.get('/', (req, res) => {
    res.status(200).send('I am MSEI')
})

const PORT = process.env.PORT || 8080;

app.listen(PORT, () => console.log(`Server aktivan... PORT ${PORT}`))