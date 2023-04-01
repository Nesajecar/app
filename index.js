const PORT = process.env.PORT || 8080;

var http = require('http');
http.createServer(function(req,res){
    res.writeHead(200,{'Content-Type':'text/html'});
    res.write('i am MSEI')
    res.end()

}).listen(PORT,() => console.log(`Server aktivan... PORT ${PORT}`))
