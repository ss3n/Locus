from flask import Flask, render_template, request
import requests
import json
app = Flask(__name__)

lookupaddr = 'http://0.0.0.0:5000'

@app.route('/')
@app.route('/publish/')
def publish():
    latitude = request.args.get('lat')
    longitude = request.args.get('lon')

    # request for region of the advertiser
    r = requests.get(lookupaddr+'/region?lat='+str(latitude)+'&lon='+str(longitude))
    publishregion = r.content
    app.logger.debug("Region of publisher: " + str(publishregion))

    # request for list of available topics
    r = requests.get(lookupaddr+'/topiclist')
    topiclist = json.loads(r.content)
    for topic in topiclist:
        app.logger.debug("Topic: " + str(topic))

    return render_template('publish-ad.html', topiclist=topiclist)


if __name__ == '__main__':
    app.debug=True
    app.run(host="0.0.0.0", port=5100)
