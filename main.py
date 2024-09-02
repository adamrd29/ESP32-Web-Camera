from utime import sleep, sleep_ms
import camera
import picoweb
from machine import Pin, PWM
import config
import network

with open("index.html", "r") as html:
    html_content = html.read()

panPos = 90
tiltPos = 90

panServo = PWM(Pin(14), freq=50, duty=panPos)
tiltServo = PWM(Pin(13), freq=50, duty=tiltPos)

def index(req, resp):
    
    global panPos, tiltPos
    
    if req.method == "POST":
        yield from req.read_form_data()
        data = req.form
        direction = data.get('direction', None)
        if direction == "down" and tiltPos < 111:
            for i in range(10):
                tiltPos += 1
                tiltServo.duty(tiltPos)
                sleep_ms(20)
            
        elif direction == "up" and tiltPos > 69:
            for i in range(10):
                tiltPos -= 1
                tiltServo.duty(tiltPos)
                sleep_ms(20)
            
        elif direction == "left" and panPos < 106:
            for i in range(15):
                panPos += 1
                panServo.duty(panPos)
                sleep_ms(20)
            
        elif direction == "right" and panPos > 44:
            for i in range(15):
                panPos -= 1
                panServo.duty(panPos)
                sleep_ms(20)
        
        elif direction == "center":
            if tiltPos > 90:
                for i in range(tiltPos - 90):
                    tiltPos -= 1
                    tiltServo.duty(tiltPos)
                    sleep_ms(20)
                    
            elif tiltPos < 90:
                for i in range(90 - tiltPos):
                    tiltPos += 1
                    tiltServo.duty(tiltPos)
                    sleep_ms(20)
                    
            if panPos > 90:
                for i in range(panPos - 90):
                    panPos -= 1
                    panServo.duty(panPos)
                    sleep_ms(20)
            
            elif panPos < 90:
                for i in range(90 - panPos):
                    panPos += 1
                    panServo.duty(panPos)
                    sleep_ms(20)
        
        print(f"pan: {panPos} | tilt: {tiltPos}")
        
    yield from resp.awrite(html_content)

        
def stream(req, resp):
    yield from picoweb.start_response(resp, content_type="multipart/x-mixed-replace; boundary=frame")
    
    while True:
        buf = camera.capture()
        frame_data = b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + buf + b'\r\n'
        yield from resp.awrite(frame_data)


ROUTES = [
    ("/", index),
    ("/stream", stream),
]


if __name__ == '__main__':
    #Camera Initialisation
    camera.init(0, d0=4, d1=5, d2=18, d3=19, d4=36, d5=39, d6=34, d7=35,
        format=camera.JPEG, framesize=camera.FRAME_VGA, 
        xclk_freq=camera.XCLK_10MHz,
        href=23, vsync=25, reset=-1, pwdn=-1,
        sioc=27, siod=26, xclk=21, pclk=22, fb_location=camera.PSRAM)

    #WiFi connection
    station = network.WLAN(network.STA_IF)
    station.active(True)
    station.connect(config.ssid, config.password)
    timeout = 0
    while not station.isconnected():
      sleep(1)
      if timeout > 5:
          print('Connection failed')
          break
      timeout += 1

    if station.isconnected():
        print('Connection successful')
        print(station.ifconfig())

    #Start Server
    app = picoweb.WebApp(__name__, ROUTES)
    app.run(debug=1, port=80, host="0.0.0.0")
