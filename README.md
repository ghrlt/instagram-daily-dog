Wanna post a duck everyday in your Instagram story? This gist is made for you!

This program is made to be run as a Linux service, still, you can use the code in `app.py` alone.


# Installation as a Linux service
```
git clone https://gist.github.com/d4f2a315bc81dc631c7881fd497ac881.git
mv d4f2a315bc81dc631c7881fd497ac881 ig-dailyduck
cd ig-dailyduck
mv '~.env' .env
```
Before continuing, you will have to set the value of `WorkingDirectory` in `ig-dailyduck.service` file by the path to the location of ig-dailyduck folder.
Once you did, and only then, you can continue

```
mv ig-dailyduck.service /etc/systemd/system
mv ig-dailyduck.timer /etc/systemd/system
```
Now open `.env` in your preferred editor and fill in your details. Then, enable the service.

```
systemctl daemon-reload
systemctl enable ig-dailyduck --now
```
Enjoy your daily duck, default posted at 5pm