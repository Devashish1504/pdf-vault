# Metadata Information Leakage

## The Flaw
PDF files contain metadata tags such as:
- `/Author`: Who created the file.
- `/Creator`: The software used (e.g., "Microsoft Word 2016").
- `/Producer`: The conversion engine (e.g., "Quartz PDFContext").
- `/CreationDate`: Timestamp.
- `/ModDate`: Timestamp.

PDFVault's `/metadata` route simply dumps this information.

## Impact
1. **OS Fingerprinting**: Seeing "Quartz" implies macOS. Seeing "Microsoft Word" implies Windows.
2. **Software Versioning**: Known vulnerabilities in specific versions of Adobe Acrobat or Word can be targeted if the version is leaked.
3. **Internal Usernames**: The Author field often defaults to the logged-in system username (e.g., `corp\alice_admin`), revealing valid internal account names for phishing or login attacks.
4. **Internal Paths**: Sometimes metadata or embedded streams contain absolute file paths (e.g., `C:\Users\admin\Documents\Confidential\ProjectX.docx`).

## Mitigation
- **Scrub Metadata**: Use tools like `mutool` or libraries to strip all non-essential metadata before publishing or sharing files.
- **Sanitization**: Overwrite the Producer/Creator fields with generic values.
