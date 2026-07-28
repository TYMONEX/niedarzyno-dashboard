from flask import Flask, request
from datetime import datetime

app = Flask(__name__)

visits = 0


@app.route("/")
def home():
    global visits
    visits += 1

    ip = request.remote_addr
    print(f"[{datetime.now().strftime('%H:%M:%S')}] IP: {ip}")

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
    font-family:Arial, sans-serif;
}}


body {{

    height:100vh;
    overflow:hidden;

    color:white;

    background:black;

    animation:flicker 4s infinite;

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

    background:
    rgba(0,0,0,.55);

    z-index:-2;

}}



/* scanlines */

body::after {{

    content:"";

    position:fixed;

    inset:0;


    background:

    repeating-linear-gradient(
    0deg,
    rgba(255,255,255,.04),
    rgba(255,255,255,.04) 1px,
    transparent 1px,
    transparent 4px
    );


    pointer-events:none;

    z-index:20;

}}




/* START */


#start {{

    position:fixed;

    inset:0;


    display:flex;

    justify-content:center;

    align-items:center;


    background:

    radial-gradient(
    circle,
    #111,
    #000
    );


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



#loading {{

    margin-top:30px;

    letter-spacing:4px;

    animation:pulse 1s infinite;

}}



.bar {{

    width:350px;

    height:18px;


    margin:30px auto;


    background:#222;


    border-radius:20px;


    overflow:hidden;


    border:1px solid cyan;

}}



#progress {{

    height:100%;

    width:0%;


    background:

    linear-gradient(
    90deg,
    red,
    blue
    );


    box-shadow:

    0 0 20px cyan;

}}



button {{

    margin-top:30px;


    padding:18px 60px;


    border:none;

    border-radius:50px;


    background:

    linear-gradient(
    90deg,
    red,
    blue
    );


    color:white;


    font-size:25px;


    cursor:pointer;


    box-shadow:

    0 0 30px red;

}}



button:hover {{

    transform:scale(1.1);

}}




/* PANEL */


.card {{

    position:absolute;


    top:50%;

    left:50%;


    transform:

    translate(-50%,-50%);


    width:450px;


    padding:40px;


    text-align:center;


    background:

    rgba(0,0,0,.65);


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

    box-shadow:

    0 0 30px #5865F2;

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



@keyframes pulse {{

50% {{
opacity:.5;
}}

}}



@keyframes flicker {{

0%,100% {{
filter:none;
}}

50% {{
filter:brightness(1.2);
}}

}}



@keyframes fadeout {{

from {{
opacity:1;
}}

to {{
opacity:0;
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


<p id="loading">

INITIALIZING SYSTEM...

</p>



<div class="bar">

<div id="progress"></div>

</div>



<p id="percent">

0%

</p>



<button id="enter" onclick="enter()" style="display:none">

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



<div id="discordBox" style="display:none;">

<a class="discord"
href="https://discord.gg/dkZPcMeqMD"
target="_blank">

💬 DISCORD

</a>

</div>



</div>





<script>


let progress = 0;


let bar =
document.getElementById("progress");


let percent =
document.getElementById("percent");


let btn =
document.getElementById("enter");



let load=setInterval(()=>{{


progress += Math.floor(Math.random()*10)+5;


if(progress>=100){{


progress=100;


clearInterval(load);


document.getElementById("loading").innerHTML=

"SYSTEM READY";


btn.style.display="inline-block";


}}


bar.style.width=progress+"%";

percent.innerHTML=progress+"%";


}},300);





function enter(){{


let start =
document.getElementById("start");


start.style.animation="fadeout 1s";



setTimeout(()=>{{


start.style.display="none";


let video =
document.getElementById("bg");


video.volume=0.25;


video.play();

setTimeout(()=>{

document.getElementById("discordBox").style.display="block";

},4800);



}},1000);



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
