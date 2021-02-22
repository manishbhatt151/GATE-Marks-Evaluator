# GO's offline response sheet parser

### Generated file: [`sample_result.json`](./sample_result.json)

## Requirements

`python3`, `python3-pip` can be installed by,

```sh
$ sudo apt install python3 python3-pip
```

## Quickstart

1. Installed the required packages

```sh
$ pip3 install requests requests_html
```
or
```
$ pip3 install -r requirements.txt
```
2. Run the script by giving proper arguments
```
$ python3 main.py -r <RESPONSE_URL> -k <KEY_URL> -o <FILE_NAME>
```

3. Getting help
```cmd
$ python3 parse.py -h
usage: parse.py [-h] [-r RESPONSE_URL] [-k ANSWER_KEY_URL] [-o FILE_NAME]

Parses candidate's response sheet, calculates marks, and stores results as JSON.

optional arguments:
  -h, --help            show this help message and exit
  -r RESPONSE_URL, --response RESPONSE_URL
                        Candidate's response key URL.
  -k ANSWER_KEY_URL, --key ANSWER_KEY_URL
                        Answer key URL.
  -o FILE_NAME          Print output to file.
```


## Notes

1. Tested on my response sheet, cross checked with Pragy's. Results match.

2. if `-o` is not provided, the program prints output to `stdout`.

3. JSON output is of structure:

```
[
    {
        "question_mark": "1",
        "question_short_id": "g5",
        "question_type": "MCQ",
        "question_long_id": "8232513095",
        "response_given": "C",
        "actual_answer": "C",
        "subject_id": "1",
        "marks_obtained": 1.0
    }
]
```

4. Please pass the urls inside "" script is failing while parsing the links

```
    python main.py -r "link_to_response_sheet" -k "link_to_key" -o file_name
```
