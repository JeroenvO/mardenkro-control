var socket = null;
var isopen = false;
$(document).ready(function () {

    var canvas = document.getElementById('canvas');
    var ctx = canvas.getContext('2d');
    var w = $('.container').width();
    var h = w * 0.8;
    $('#canvas').width(w).height(h);

    ctx.canvas.width = w;
    ctx.canvas.height = h;

    function drawField() {
        ctx.clearRect(0, 0, w, h);
        ctx.strokeStyle = '#000';
        ctx.fillStyle = '#0b0';
        ctx.beginPath();
        ctx.fillRect(0, 0, w, h);
        ctx.stroke();
        ctx.lineWidth = 5;
        //horizontal line below
        ctx.beginPath();
        ctx.moveTo(0, h);
        ctx.lineTo(w, h);
        ctx.stroke();
        //notch in the center
        ctx.beginPath();
        ctx.moveTo(w / 2, h);
        ctx.lineTo(w / 2, h - h / 10);
        ctx.stroke();
    }

    function drawLine(offset, angle) {
        drawField();
        //line
        ctx.beginPath();
        var x_o = offset * w / 2 + w / 2;
        ctx.moveTo(x_o - 30, h);
        ctx.lineTo(x_o + 30, h);
        var x_e = x_o + Math.tan(angle) * h;
        ctx.lineTo(x_e + 10, 0);
        ctx.lineTo(x_e - 10, 0);
        ctx.closePath();
        ctx.lineWidth = 10;
        ctx.strokeStyle = '#efefef';
        ctx.fillStyle = '#efefef';
        ctx.lineStyle = '#000';
        ctx.stroke();
        ctx.fill();
    }

    function timestamp(){
        var dt = new Date();
        var m = dt.getMinutes();
        var s = dt.getSeconds();
        if(m<10){
            m = '0'+m;
        }
        if(s<10){
            s = '0'+m;
        }
        return dt.getHours() + ':' + m + ':' + s + '; '
    }
    var hostname = window.location.hostname;
    socket = new WebSocket("ws://" + hostname + ":9000");
    socket.binaryType = "arraybuffer";
    socket.onopen = function () {
        console.log("Connected!");
        $("#update").prepend(timestamp() + 'Connected! <br />');
        isopen = true;
        drawField();
    };
    socket.onmessage = function (e) {
        if (e.data.startsWith('L')) { //line poinot
            var d = JSON.parse(e.data.substr(1));
            if (typeof d[1] === 'string') {
                $('#info').text(d[1])
            } else {
                $('#info').text('# lines [0-100]: ' + d[3].toString());
                drawLine(d[1], d[2]);
            }
        } else if (e.data.startsWith('U')) {
            $("#update").prepend(timestamp() + e.data.substr(1) + '<br />');
        } else if (e.data.startsWith('T')) {
            $("#time").text('Refresh rate: '+ e.data.substr(1) + 'Hz');
        } else if (e.data.startsWith('A')) {
            var d = JSON.parse(e.data.substr(1));
            $("#curarm").text(d[1]);
            $("#curspeed").text('Left: '+ d[0] + ' Right: '+ d[1]);
        } else{
            console.log("Received: "+e.data)
        }
    };
    socket.onclose = function (e) {
        console.log("Connection closed.");
        $("#update").prepend(timestamp() + 'Raspberry connection lost! <br />');
        socket = null;
        isopen = false;
    };

    $('a.btn').click(function () {
        var s = $('#speedslide')[0].value;
        var v = $(this).data('dir');
        v = v.map(function (x) {
            return (x * s)
        });  //speed and direction
        var pomp = 0;
        var threeway = 0;
        var arm = parseInt($('#arm')[0].value);
        $("#setarm").text(arm);
        $("#setspeed").text('Left: '+ v[0] + ' Right: '+ v[1]);
        var msg = 'C' + JSON.stringify([v[0], v[1], arm, pomp, threeway]);
        console.log(msg);
        socket.send(msg)
    });

});
