A command line video downloader for hqpornero.com

İnstallation:

```git clone https://github.com/covrc/hqpornero-downloader```

```cd hqpornero-downloader ; pip install -r requirements.txt```

You need to install firefox to use this code so install firefox to your system.
In linux

```apt install firefox```

or

```pacman -S firefox```

or use your distro's package manager

In windows
Download firefox from https://www.firefox.com/

You ***may*** need geckodriver, before installing geckodriver, try to run code with only firefox installed

In linux download ```geckodriver``` package with your distro's package manager if it is needed.

In windows
Download geckodriver from https://geckodriver.com/download/ and add geckodriver.exe to path environment variable

After installing dependencies, you can download from hqpornero.com

```python hqpornero-dl.py -h``` for additional help

Downloader uses wget as default download option but with -r parameter it can download with requests library without need of any dependency

```python hqpornero-dl URL -r``` uses requests downloader and does not need wget to download
