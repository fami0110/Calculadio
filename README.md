# Calculadio
_Enchanced Calculator using Speech to Text Recognition_

Desktop app build using customtkinter for you that lazy to navigate through the calculator UI. This app currently I set for indonesian. If you want to change the language, go to `record()` and `process_stream()` method.

## Technologies Used

- [Customtkinter](https://customtkinter.tomschimansky.com/)
- [SpeechRecognition](https://pypi.org/project/SpeechRecognition/)

## List speech command

| Commands | Action |
| --- | --- |
| `tambah`, `plus` | addition |
| `kurang`, `min` | subtraction |
| `kali` | multiplication |
| `bagi` | division |
| `kurung` | open bracket |
| `tutup` | close bracket |
| `hapus` | delete last character |
| `salah`, `kembali`, `back` | delete last token |
| `bersih`, `clear`, `reset` | clear all |
| `berhenti`, `stop` | stop listening |

## How to use



But if you want to try directly from sourcecode, you can follow this step:

1. Clone the repository:

    ```bash
    $ git clone https://github.com/fami0110/Calculadio.git
    $ cd Calculadio
    ```

2. Install dependencies:

    ```bash
    $ pip install -r requirements.txt
    ```

3. Type this command to run the app

    ```bash
    $ python app.py
    ```