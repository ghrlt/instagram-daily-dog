# Instagram Story Daily Dog
Wanna post a dog everyday in your Instagram story? This repo is made for you!


# Installation as a Linux service
Download
```
git clone https://github.com/ghrlt/instagram-daily-dog.git
cd instagram-daily-dog
```

Install requirements
```
pip install -r requirements.txt
```

Before continuing, you will have to set the value of `WorkingDirectory` in `ig-dailydog.service` file by the path to the lodogion of ig-dailydog folder.
Once you did, and only then, you can continue
```
mv ig-dailydog.service /etc/systemd/system
mv ig-dailydog.timer /etc/systemd/system
```

Now open `.env` in your preferred editor and fill in your details. (If you do not have 2FA on your account, do not touch `INSTAGRAM_2FA_SEED`.

Then, enable the service.
```
systemctl daemon-reload
systemctl enable ig-dailydog --now
```
Enjoy your daily dog, default posted at 5pm UTC

# FAQ

#### What is 'INSTAGRAM_2FA_SEED'?
If you have enabled 2FA on your Instagram account, and you set it up through an auth app like Authy or Google Authentidogor, you were provided with a QRcode / a seed! 
This seed allow to generate the 2FA 6 digits code, required to login in your account. You can found it, either when setting up 2FA or in your auth applidogion (Usually, you'll have an "Edit" button on the account)

#### Is it safe for my Instagram account?
Automating anything on Instagram is against their TOS, thus, I cannot take any responsability if the usage of this program leads to a ban.
<br>
However, the [library used](https://github.com/adw0rd/instagrapi) is built to avoid as much as possible any detection. Furthermore, as this program is only posting once a day, it shouldn't be flagged.


If you are worried for your credentials, which you should always be, you can check by yourself the code of both this program and [instagrapi](https://github.com/ghrlt/instagram-daily-dog).
