import datetime
import os
import queue
from urllib.error import HTTPError

from apiclient.errors import HttpError
import cv2
from flask import Flask, Response, request, jsonify, current_app

from pynopticon import Pynopticon
from pynopticon.upload_video import get_authenticated_service

qs = [] # list of frame queues

if os.environ.get("CLIENT_SECRETS_FILE"):
  youtube = get_authenticated_service(os.environ.get("CLIENT_SECRETS_FILE"))
else:
  youtube = None

sendgrid_api_key = os.environ.get("SENDGRID_API_KEY")
sendgrid_from_email = os.environ.get("SENDGRID_FROM_EMAIL")
sg = None
if any([sendgrid_api_key, sendgrid_from_email]):
  if all([sendgrid_api_key, sendgrid_from_email]):
    import sendgrid
    import sendgrid.helpers.mail
    sg = sendgrid.SendGridAPIClient(api_key=sendgrid_api_key)
  else:
    raise Exception("Must specify all or none of SENDGRID_API_KEY, SENDGRID_FROM_EMAIL")

app = Flask(__name__)


def new_frame_handler(frame):
  for q in qs:
    q.put(frame)

cam = int(os.environ.get("CAM", 0))
num_frames = int(os.environ.get("RECORD_FRAMES", 100))
width = int(os.environ.get("WIDTH", 640))
height = int(os.environ.get("HEIGHT", 480))

def generate(p):
  try:
    # create a queue for this client
    q = queue.Queue(maxsize=p.record_frames)
    qs.append(q)
    print("open queue: ", len(qs))

    while True:
      frame = q.get()
      ret, buffer = cv2.imencode(".jpg", frame)
      if not ret:
        continue
      frame = buffer.tobytes()
      yield (b'--frame\r\n'
             b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
  except Exception as e:
    print("e", e)
  finally:
    qs.remove(q)
    print("down to ", len(qs))


@app.route('/')
def index():
  return Response(generate(current_app.p), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/stop', methods=["POST"])
def stop():
  current_app.p.stop()
  return jsonify({"status": "ok"})

@app.route('/save', methods=["POST"])
def save():
  time = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
  fn = time + ".avi"
  try:
    upload = (request.args.get("upload") == "true")
    emails = request.args.get("email")
    if emails is not None:
      emails = emails.split(",")
    do_email = (emails is not None) and (len(emails) > 0)

    try:
      vidid = current_app.p.save(
        outname=fn,
        upload=upload,
        mail_to=[emails] if do_email else None,
        mail_from=(sendgrid_from_email if do_email else None),
      )
    except HTTPError as e:
      return jsonify({"status": "failed", "message": "upload or mailing failed: " + str(e)})

    if upload:
      if vidid is None:
        return jsonify({"status": "failed", "message": "Upload failed"})

      vidurl = "https://www.youtube.com/watch?v=" + vidid
      return jsonify({"status": "ok", "video_url": vidurl})
  except HttpError as e: 
    return "An HTTP error %d occurred when uploading: %s" % (e.resp.status, e.content)

  return jsonify({"status": "ok", "filename": fn})

@app.route('/start', methods=["POST"])
def start():
  current_app.p.start()
  return jsonify({"status": "ok"})

def main():
  host = os.environ.get("HOST", "0.0.0.0")
  port = int(os.environ.get("PORT", 4004))
  app.p = Pynopticon(
    width=width,
    height=height,
    new_frame_callback=new_frame_handler,
    cam=cam,
    record_frames=num_frames,
    youtube=youtube,
    sg=sg)
  app.p.start()
  app.run(host=host, port=port, threaded=True)

if __name__ == "__main__":
  main()

