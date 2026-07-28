from flask import Flask, request
from datetime import datetime

app = Flask(__name__)

visits = 0


@app.route("/")
def home():
    global visits
    visits += 1

    ip = request.remote_addr
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Wejście z IP: {ip}")

    return f"""
<!DOCTYPE html>
<html>

<head>

<title>Niedarzyno</title>

<style>

* {{
    margin:0;
    padding:0;
    box-sizing:border-box;
    font-family:Arial,sans-serif;
}}


body {{
    height:100vh;
    overflow:hidden;
    color:white;
}}



#bg {{
    position:fixed;
    width:100%;
    height:100%;
    object-fit:cover;
    z-index:-3;
}}



.overlay {{
    position:fixed;
    inset:0;
    background:rgba(0,0,0,0.55);
    z-index:-2;
}}



#start {{
    position:fixed;
    inset:0;

    display:flex;
    justify-content:center;
    align-items:center;

    background:#000;

    z-index:10;
}}



.start-box {{
    text-align:center;
}}



.start-title {{
    font-size:70px;
    font-weight:900;

    text-shadow:
    5px 0 red,
    -5px 0 cyan;

    animation:glitch .8s infinite;
}}



button {{
    margin-top:40px;

    padding:18px 55px;

    border:none;
    border-radius:50px;

    background:
    linear-gradient(90deg,#ff003c,#004cff);

    color:white;

    font-size:25px;

    cursor:pointer;

    box-shadow:
    0 0 30px red;
}}



button:hover {{
    transform:scale(1.1);
}}




.card {{
    position:absolute;

    top:50%;
    left:50%;

    transform:translate(-50%,-50%);


    width:450px;

    padding:40px;

    text-align:center;


    background:rgba(0,0,0,0.65);

    border-radius:30px;


    backdrop-filter:blur(10px);


    box-shadow:

    0 0 30px red,
    0 0 60px blue;
}}



h1 {{

    font-size:50px;

    text-shadow:
    3px 0 red,
    -3px 0 cyan;

}}



.status {{

    margin:25px;

    padding:15px;

    background:#22c55e;

    border-radius:15px;

    font-weight:bold;

}}



.discord {{

    display:inline-block;

    margin-top:25px;

    padding:15px 30px;

    background:#5865F2;

    color:white;

    text-decoration:none;

    border-radius:20px;

    font-size:20px;

}}



.discord:hover {{
    box-shadow:0 0 30px #5865F2;
}}



@keyframes glitch {{

0% {{
transform:translate(0);
}}

50% {{
transform:translate(5px,-3px);
}}

100% {{
transform:translate(0);
}}

}}

</style>

</head>


<body>


<video id="bg" loop>

<source src="/static/edit.mp4" type="video/mp4">

</video>


<div class="overlay"></div>



<div id="start">

<div class="start-box">

<div class="start-title">
🕸️ NIEDARZYNO
</div>


<button onclick="enter()">
WEJDŹ
</button>


</div>

</div>




<div class="card">


<h1>
NIEDARZYNO
</h1>


<div class="status">
🟢 ONLINE
</div>


<p>
Niedarzyno Dashboard
</p>


<p>
👥 Wejścia: {visits}
</p>


<p>
🕒 {datetime.now().strftime("%H:%M:%S")}
</p>



<a class="discord"
href="https://discord.gg/dkZPcMeqMD"
target="_blank">

💬 DOŁĄCZ DO DISCORDA

</a>


</div>





<script>

function enter() {{

let start=document.getElementById("start");

start.style.display="none";


let video=document.getElementById("bg");

video.volume=0.25;

video.play();

}}

</script>


</body>

</html>
"""


if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000
    )
