# DMS BBOX Validator
A tool for manual validation of bounding box annotations.

<img src="public/favicon.jpg" height="200">

## Installation
Go to [artifactory](https://artifactory.sddc.mobileye.com/ui/packages) and follow the instructions to setup a pip access.
![](docs/jfrog.setup.gif)

Run `pip install dms-annotator`

You should now be able to run:
```
dms-validator <video.mp4> <annotation.json>
```

Where `<video.mp4>` is a path to the relevant clip and `<annotation.json>` is the bounding box annotation in a `xyxy` format, e.g:
```json
[
    [0, 2, 13, 54],
    [1, 3, 4, 17],
    [34, 12, 54, 28]
]
```

If you would like to generate a sample (face) `annotation.json` file you can run:
```
dms-annotate <video.mp4>
```

Once you run the command 
```
dms-validator <video.mp4> <annotation.json>
```
A local web-server is launched and you can interact with it via your browser. If you run it on a remote machine you will have to setup [port forwarding](https://linuxize.com/post/how-to-setup-ssh-tunneling/), if you run it from VsCode's terminal this should happen automatically.
![](docs/demo.gif)