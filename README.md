# Banking QA Automation — ProCredit Bank & ParaBank

**Python · Selenium · pytest · Requests · Page Object Model · Jenkins · Allure**

## პროექტის შესახებ

ეს პროექტი შევქმენი საბანკო ვებაპლიკაციისა და REST API-ის ავტომატიზებული ტესტირების პრაქტიკული დავალების ფარგლებში. ჩემი მიზანი იყო არა მხოლოდ UI ელემენტების შემოწმება, არამედ ბიზნესლოგიკის გადამოწმებაც: ანგარიშის ბალანსი, თანხის მოძრაობა, ტრანზაქციების ისტორია და უარყოფითი სცენარის მოსალოდნელი შედეგი.

სამუშაო ორ გარემოდ გავყავი:

- **[ParaBank Demo](https://parabank.parasoft.com/parabank/)** — დემო გარემო, სადაც სრულფასოვანი გადარიცხვის ტესტირება შესაძლებელია UI-ითა და API-ით.
- **[ProCredit Bank Internet Banking](https://online.procreditbank.ge/login)** — რეალური საბანკო გარემო, რომლის ტესტირებასაც უსაფრთხოების დამატებითი შეზღუდვები დავუწესე.

სცენარების შერჩევისას ყურადღება გავამახვილე საბანკო სისტემისთვის მნიშვნელოვან რისკებზე: ავტორიზაციის სისწორე, თანხის არასწორი ჩამოჭრა, ანგარიშებს შორის ბალანსების შეუსაბამობა და არასწორი ტრანზაქციის დამუშავება.

## ავტომატიზებული სცენარები

| გარემო | სცენარი | რა მოწმდება |
|---|---|---|
| ParaBank | Smoke | ავტორიზაცია და Accounts Overview; გადარიცხვის გარეშე |
| ParaBank | UI Transfer | შიდა გადარიცხვა, გამგზავნისა და მიმღების ბალანსები, Debit/Credit ჩანაწერები |
| ParaBank | API Transfer | `GET → POST → GET`, HTTP სტატუსები და ორივე ანგარიშის ბალანსის ცვლილება |
| ProCredit | Desktop Login | მომხმარებლის ავტორიზაცია SMS OTP-ით |
| ProCredit | Mobile Web Login | იგივე ავტორიზაცია Chrome-ის 414×896 responsive რეჟიმში |
| ProCredit | Desktop/Mobile Negative Transfer | არასაკმარისი თანხის სცენარი, მოსალოდნელი შეტყობინება და უცვლელი ბალანსი; მხოლოდ სპეციალური ნებართვით |
| Framework | Unit Tests | API Client-ის, კონფიგურაციის, არქიტექტურული წესებისა და დამხმარე ლოგიკის შემოწმება |

**ParaBank-ის Transfer ტესტი** მხოლოდ წარმატების შეტყობინებას არ ენდობა. ოპერაციამდე და ოპერაციის შემდეგ ვკითხულობ ორივე ანგარიშის ბალანსს და ვამოწმებ, რომ ერთ ანგარიშს ზუსტად შესაბამისი თანხა ჩამოეჭრა, მეორეს კი დაემატა. UI სცენარში დამატებით ვამოწმებ Debit/Credit ისტორიას. თანხებთან სამუშაოდ ვიყენებ `Decimal` ტიპს.

**ProCredit-ის Negative Transfer** ცალკე მაქვს გამოყოფილი: მისი საბოლოო ეტაპი რეალურ საბანკო ფორმაზე ერთჯერად Submit-ს შეიცავს. ამიტომ ტესტი ნაგულისხმევად გამორთულია; მისი შესრულება შეიძლება მხოლოდ უფლებამოსილ, ხელით დამტკიცებულ გარემოში. ჩვეულებრივი CI Pipeline ამ სცენარს არ უშვებს. ეს შეზღუდვა განზრახ მივიღე რეალურ ანგარიშებთან მუშაობის რისკის გამო.

## არქიტექტურა

Framework ავაწყვე **Page Object Model (POM)** პრინციპით და პასუხისმგებლობები გავყავი ფენებად:

```text
Test → Steps → Pages → Elements / DriverUtils

banking-qa-automation/
├── tests/                  # UI სცენარები
├── api_tests/              # REST API სცენარები
├── unit_tests/             # იზოლირებული Unit ტესტები
├── steps/                  # სცენარის ორკესტრაცია
├── pages/                  # ლოკატორები და Selenium-ის ინტერაქციები
├── elements/               # საერთო UI ელემენტების კლასები
├── api/                    # Requests API Client
├── managers/               # DriverManager / BrowserFactory
├── utils/                  # Wait-ები, Test Data, OTP, Reporting
├── scripts/                # დიაგნოსტიკა და ლოკალური დამხმარე სკრიპტები
├── resources/config.json   # საიტების საბაზისო მისამართები
├── reports/                # pytest-ის რეპორტინგის მოდული
├── Jenkinsfile             # ძირითადი Pipeline
├── Jenkinsfile.smoke       # ცალკე Smoke Pipeline
├── Jenkinsfile.api         # ცალკე API Pipeline
├── Jenkinsfile.procredit   # მხოლოდ ხელით გასაშვები Login Pipeline
├── Jenkinsfile.procredit-negative # მკაცრად შეზღუდული live-bank Pipeline
├── requirements-ci.txt
├── pytest.ini
└── .env.example
```

- **Tests:** მხოლოდ შესაბამის Steps-ს იძახებს.
- **Steps:** განსაზღვრავს ბიზნესსცენარის ნაბიჯების თანმიმდევრობას.
- **Pages:** ინახავს ლოკატორებს, UI მოქმედებებსა და გვერდის დონის შემოწმებებს.
- **Elements / DriverUtils:** საერთო Selenium ოპერაციები და Explicit Wait-ები.
- **API Client:** განცალკევებულია Selenium-ისგან, ამიტომ API ტესტს ბრაუზერი არ სჭირდება.

ამ მიდგომით ლოკატორის ცვლილება ძირითადად Page კლასში რჩება და სცენარის კოდი უფრო მარტივად იკითხება.

## გამოყენებული ტექნოლოგიები

`Python`, `Selenium WebDriver`, `pytest`, `Requests`, `Allure`, `Jenkins`, `Git/GitHub`, `Chrome DevTools Protocol`, `Android Termux:API`, `ADB`, `SSH`.

Mobile ტესტები ამოწმებს **responsive ვებვერსიას**, და არა ნატიურ Android აპს. რეალური Android ტელეფონი გამოიყენება მხოლოდ ProCredit-ის SMS OTP-ის მისაღებად.

## ლოკალურად გაშვება

პროექტს ძირითადად ვუშვებ **Windows / PowerShell** გარემოში. საჭიროა Python 3, Google Chrome და Selenium-ისთვის ხელმისაწვდომი ბრაუზერი. ParaBank-ის ტესტებისთვის ასევე უნდა მუშაობდეს ParaBank Demo (ჩემს ლოკალურ გარემოში — Tomcat-ზე `http://localhost:8081/parabank`). სხვა მისამართის შემთხვევაში შეიცვლება `PARABANK_BASE_URL`.

პროექტის ძირითადი საქაღალდიდან:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-ci.txt
Copy-Item .env.example .env
```

`.env`-ში შეიყვანეთ საკუთარი **დემო** მომხმარებელი და ორი განსხვავებული დემო ანგარიშის ID. ეს ფაილი `.gitignore`-შია და რეპოზიტორიაში არ იტვირთება. `.env.example` შეიცავს მხოლოდ ნიმუშებსა და გამორთულ უსაფრთხოების ფლაგებს.

### ძირითადი კონფიგურაცია

| ცვლადი | დანიშნულება |
|---|---|
| `PARABANK_BASE_URL` | ParaBank-ის გაშვებული ინსტანციის URL |
| `PARABANK_USERNAME`, `PARABANK_PASSWORD` | დემო მომხმარებლის ავტორიზაცია |
| `PARABANK_FROM_ACCOUNT`, `PARABANK_TO_ACCOUNT` | ორი განსხვავებული დემო ანგარიშის ID |
| `PARABANK_TRANSFER_AMOUNT` | დემო გადარიცხვის თანხა, მაგალითად `1.00` |
| `PARABANK_API_TRANSFER_RUN` | API POST სცენარის ცალსახა ჩართვა (`YES`); ნაგულისხმევად `NO` |
| `PRO_CREDIT_RUN` | რეალური ბანკის Login ტესტების ჩართვა; ნაგულისხმევად `0` |
| `PRO_CREDIT_NEGATIVE_SUBMIT` | live-bank საბოლოო Submit-ის დამატებითი კონტროლი; ნაგულისხმევად `NO` |
| `PRO_CREDIT_MOBILE_NEGATIVE_SUBMIT` | მობილური live-bank Submit-ის დამატებითი კონტროლი; ნაგულისხმევად `NO` |
| `TERMUX_SSH_USER`, `TERMUX_SSH_KEY` | Android-ის SSH კავშირის ლოკალური კონფიგურაცია |
| `PROCREDIT_SMS_SENDER`, `PROCREDIT_OTP_LENGTH` | SMS კოდის გამომგზავნი და ფორმატი |

### ტესტების გაშვების ბრძანებები

**Unit ტესტები — ბრაუზერის გარეშე:**

```powershell
.\.venv\Scripts\python.exe -m pytest unit_tests -v
```

**ParaBank Smoke — გადარიცხვის გარეშე:**

```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_smoke_transfer_funds.py -v
```

**ParaBank UI — დემო გადარიცხვა:**

```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_transfer_funds.py -v
```

**ParaBank API Client-ის Unit ტესტები:**

```powershell
.\.venv\Scripts\python.exe -m pytest unit_tests/test_parabank_api_client.py -v
```

**ParaBank API GET → POST → GET — დემო ანგარიშების ბალანსებს ცვლის:**

```powershell
$env:PARABANK_API_TRANSFER_RUN = "YES"
.\.venv\Scripts\python.exe -m pytest api_tests/test_parabank_api_transfer.py -v
```

ამ API ტესტის გასაშვებად ParaBank უნდა იყოს ხელმისაწვდომი და `.env`-ში მითითებული ანგარიშები უნდა არსებობდეს. უსაფრთხოების მიზნით, API Client ნაგულისხმევად მხოლოდ ლოკალურ გარემოს ან დამატებით დაშვებულ ოფიციალურ დემო ჰოსტს იღებს.

### ProCredit — მხოლოდ ავტორიზებული გაშვება

ProCredit-ის ტესტებისთვის საჭიროა მოქმედი, ნებადართული ანგარიში, SMS OTP-ის მიმღები Android მოწყობილობა და გამართული `ADB → SSH → Termux:API` კავშირი. საბანკო პაროლი და OTP არასოდეს უნდა აიტვირთოს GitHub-ზე. პაროლის მიწოდება შესაძლებელია გარემოს ცვლადით ან Windows Credential Manager-ით (`scripts/set_procredit_password.py`).

ავტორიზაციის ცალკეული ტესტებია:

- `tests/test_procredit_login.py`
- `tests/test_procreditbank_mobile_login.py`

მათი შესასრულებლად საჭიროა `PRO_CREDIT_RUN=1` და შესაბამისი ლოკალური კონფიგურაცია. რეალური ბანკის Negative Transfer ტესტები დამატებით მოითხოვს ცალსახა უფლებამოსილებასა და ხელით გაშვებას; მათი ჩვეულებრივ, ავტომატურად გაშვება არ არის გათვალისწინებული.

## Jenkins / CI/CD

პროექტში შევიტანე რამდენიმე Pipeline, რათა სხვადასხვა რისკის მქონე სცენარები ერთმანეთისგან გამემიჯნა:

| Pipeline | გამოყენება |
|---|---|
| `Jenkinsfile` | Unit, ParaBank Smoke/UI/API და სურვილისამებრ, დამტკიცებული ProCredit Login |
| `Jenkinsfile.smoke` | სწრაფი Smoke შემოწმება |
| `Jenkinsfile.api` | API Unit; POST გადარიცხვა მხოლოდ `RUN_API_TRANSFER=true` შემთხვევაში |
| `Jenkinsfile.procredit` | ცალკე, ხელით გასაშვები Login / OTP |
| `Jenkinsfile.procredit-negative` | მხოლოდ ხელით დამტკიცებული რეალური ბანკის Negative Transfer |

Jenkins-ში ვიყენებ პარამეტრებს (`RUN_UNIT`, `RUN_PARABANK_SMOKE`, `RUN_PARABANK_UI`, `RUN_PARABANK_API` და სხვ.), ხოლო პაროლებსა და მომხმარებლის მონაცემებს ვაწვდი **Jenkins Credentials**-იდან და არა კოდში ჩაწერილი მნიშვნელობებით. ParaBank-ის ლოკალური ინსტანცია შესაბამის Jenkins Agent-ზეც უნდა იყოს ხელმისაწვდომი.

მიზანი იყო, რომ ერთი ტესტის ან გარემოს შეზღუდვამ სხვა ჯგუფები არ დაბლოკოს და live-bank სცენარები შემთხვევით არ გაეშვას CI-ში. რეალურ ბანკზე არ ვიყენებ ავტომატურ Retry-ს საბოლოო Submit-ის შემდეგ.

## რეპორტინგი

ტესტების შედეგებისთვის ვიყენებ `pytest`-ს, `JUnit XML`-ს და `Allure`-ს. წარუმატებელი დემო UI ტესტისას შესაძლებელია Screenshot-ის დამატება. რეალური საბანკო სესიის Screenshot, HTML ან OTP არ უნდა მოხვდეს საჯარო რეპორტში ან არტეფაქტში.

ლოკალურად Allure შედეგის მომზადება:

```powershell
.\.venv\Scripts\python.exe -m pytest unit_tests -v --alluredir=allure-results
```

თუ Allure Commandline დაყენებულია, შედეგის ნახვა შეიძლება `allure serve allure-results` ბრძანებით.

## რას ვაქცევ ყურადღებას ტესტირებისას

ამ დავალებაში ჩემთვის მნიშვნელოვანი იყო შემდეგი გადაწყვეტილებები: გადარიცხვის შედეგის გადამოწმება ორივე ანგარიშზე, UI-ისა და API-ის დამოუკიდებელი ტესტირება, სწრაფი Smoke-ის გამოყოფა, ბრაუზერზე დამოკიდებულებისა და ბიზნესლოგიკის გამიჯვნა, ასევე რეალურ საბანკო გარემოში შემთხვევითი ცვლილებების შეზღუდვა.

**შენიშვნა:** რეპოზიტორია შეიცავს ტესტების კოდს და კონფიგურაციის ნიმუშს, მაგრამ არა საბანკო ანგარიშის მონაცემებს, რეალურ პაროლებს, SMS კოდებს, SSH private key-ს ან ჩემს ლოკალურ ParaBank/Tomcat ინსტანციას. ეს დამოკიდებულებები თითოეულ გარემოში ცალკე უნდა მომზადდეს.
