## APyK - APK Backup

APyK is a program with which you will be able to backup your applications from your computer, **FREE** and better yet **WITHOUT BEING ROOT**. Without further ado, let's get started.

- [x] Backup APKs
- [ ] Restore or install APKs

## :computer: - ​Pre-requisites

Have basic knowledge of **ADB (Android Debug Bridge)**, you will need to install it, add it to the environment variables and authorize your computer to access the device.

APyK fue testeado y programado con **ADB version 1.0.32 Revision eac51f2bb6a8-android**.

## Installation from Python

You can use **APyK** from Python.

```bash
pip install apyk
```

After install type **apyk** and press **Enter**

## :arrow_heading_down: ​- Download executable

Download the latest version of **APyK** from [**HERE**](/jalkhov/apyk/releases/latest/download/asset-name.zip). After downloading extract and run the **apyk.exe** file located in the extracted folder.

## :blue_book: - Usage

##### 👀 Remember

* Have ADB added to the system environment variables.
* Have granted permissions to the computer to access the device.
* Have the device in debug mode.
* And (of course), have the device connected to the computer via USB.

##### 🔎 App name lookup

![1.Name_Lookup](screenshots/1.Name_Lookup.PNG)

This warning is due to the fact that when listing the applications installed on your device they will look approximately as follows:

```text
org.telegram.messenger
com.whatsapp
com.facebook.lite
```

Each app in the playstore has a **unique ID**, and these are the ones that will be displayed in the list of apps, as you can see there are some that can be easily identified, however there are others whose IDs have nothing to do with the original name and for some people it is difficult to know which app corresponds, such as **Tik Tok**:

```text
com.zhiliaoapp.musically
```

Anyway, returning to the main point, if we decide to activate the option in question, APyK will look for the real name of the app based on the ID of this, and it will go from looking like we showed it before to look like this:

```text
org.telegram.messenger | Telegram
com.whatsapp | WhatsApp Messenger
com.facebook.lite | Facebook Lite
com.zhiliaoapp.musically | Tik Tok
```

Please note that this option requires an internet connection, and depending on the speed of the internet connection the list of applications will be loaded.

**NOTE**: As it says in the warning, apps that do not belong to the Play Store will not be affected, since as I mentioned before, the search is done based on the ID with which the app is registered.

At once I say that this option is courtesy of the library [**google-play-scraper**](https://github.com/JoMingyu/google-play-scraper), credits to its creator.

##### 🖥️ Main Screen

Once you have made a decision regarding the above option, if you have the above **[HERE](#-remember)**, the program will automatically start searching for the installed applications, and if everything went well, it will display the respective list.

## 💪 - Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## 📝 - License
[MIT](https://choosealicense.com/licenses/mit/)