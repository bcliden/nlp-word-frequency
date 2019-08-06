const express = require("express");
const app = express();
const { exec } = require("child_process");

const urlRegExp = new RegExp(
  /((([A-Za-z]{3,9}:(?:\/\/)?)(?:[\-;:&=\+\$,\w]+@)?[A-Za-z0-9\.\-]+|(?:www\.|[\-;:&=\+\$,\w]+@)[A-Za-z0-9\.\-]+)((?:\/[\+~%\/\.\w\-_]*)?\??(?:[\-\+=&;%@\.\w_]*)#?(?:[\.\!\/\\\w]*))?)/
);

app.use(express.json());

app.post("/freq/", (req, res) => {
  // console.log("firing off: ", `python basic_freq.py ${req.body.url}`);
  // console.log(urlRegExp.test(req.body.url));
  if (!urlRegExp.test(req.body.url)) {
    return res.status(400).json({ message: "bad url" });
  }
  exec(
    `python basic_freq.py ${req.body.url}`,
    { maxBuffer: 1024 * 500 },
    (error, stdout, stderr) => {
      if (error) {
        console.error(`exec error: ${error}`);
        return res.json({ message: "Something went wrong" });
      }
      if (stderr) {
        console.error(`stderr: ${error}`);
        return res.json({
          message: "Something went wrong"
        });
      }
      return res.send(stdout);
    }
  );
});

app.listen(3000, () => console.log("listening on 3000"));
