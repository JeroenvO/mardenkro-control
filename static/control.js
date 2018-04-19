var socket = null;
var isopen = false;
$(document).ready(function () {

    var canvas = document.getElementById('canvas');
    var context = canvas.getContext('2d');
    var w = $('.container').width();
    var h = w * 0.8;
    $('#canvas').width(w).height(h);

    context.canvas.width = w;
    context.canvas.height = h;

    function drawLine(offset, angle) {
        context.clearRect(0, 0, w, w);
        //horizontal line below
        context.beginPath();
        context.moveTo(0, h);
        context.lineTo(w, h);
        context.stroke();
        //notch in the center
        context.beginPath();
        context.moveTo(w / 2, h);
        context.lineTo(w / 2, h - h / 10);
        context.stroke();
        //line
        context.beginPath();
        var x_o = offset * w / 2 + w / 2;
        context.moveTo(x_o, h);
        var x_e = x_o + Math.tan(angle) * h;
        context.lineTo(x_e, 0);
        context.stroke();
    }


    var hostname = window.location.hostname;
    socket = new WebSocket("ws://" + hostname + ":9000");
    socket.binaryType = "arraybuffer";
    socket.onopen = function () {
        console.log("Connected!");
        isopen = true;
    };
    socket.onmessage = function (e) {
        console.log("rx: " + e.data);
        if (e.data.startsWith('L')) { //line poinot
            var d = JSON.parse(e.data.substr(1));
            if (typeof d[1] === 'string') {
                $('#info').text(d[1])
            } else {
                $('#info').text('# lines [0-100]: ' + d[3].toString());
                drawLine(d[1], d[2]);
            }
        }
    };
    socket.onclose = function (e) {
        console.log("Connection closed.");
        socket = null;
        isopen = false;
    };

    $('a.btn').click(function () {
        var s = $('#speed').value();
        var v = JSON.parse($(this).data('dir'));
        v = v * s;
        var msg = 'C' + JSON.stringify(v);
        console.log(msg);
        socket.send(msg)
    });

});
