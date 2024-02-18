help_examples = """
+---------------+
| Pipe as input |
+---------------+

$ echo '{"name":"Jay Neal", "address": "42 Main St 94111"}' | pt -i "Split firstname and lastname" -i "remove the address"

{"first_name": "Jay", "last_name": "Neal"}

+-----------------------------+
| Multi lines with JSON Lines |
+-----------------------------+

$ cat << EOF > data.jsonl
{"name":"John Doe","date_of_birth":"1980-01-01", "address": "123 Main St"}
{"name":"Jane Smith","date_of_birth":"1990-02-15", "address": "456 Main St"}
{"name":"Jay Neal","date_of_birth":"1993-07-27", "address": "42 Main St 94111"}
{"name":"Lisa Ray","date_of_birth":"1985-03-03", "address": "789 Elm St"}
EOF

$ cat data.jsonl | pt -i "Split firstname and lastname" -i "remove the address"

{"date_of_birth": "1980-01-01", "first_name": "John", "last_name": "Doe"}
{"date_of_birth": "1990-02-15", "first_name": "Jane", "last_name": "Smith"}
{"date_of_birth": "1993-07-27", "first_name": "Jay", "last_name": "Neal"}
{"date_of_birth": "1985-03-03", "first_name": "Lisa", "last_name": "Ray"}

+---------------+
| File as input |
+---------------+

$ cat << EOF > invoice.json
{"products":[
  {"name":"Laptop","price":1000},
  {"name":"Smartphone","price":600},
  {"name":"Headphones","price":70}
]}
EOF

$ pt --file invoice.json \\
-i 'give me the invoice total price' \\
-i 'give me the field invoice_total only'

{"invoice_total": 1670}

"""

epilog_example = """
Example:
\n\n
$ echo '{"name":"Jay Neal", "address": "42 Main St 94111"}' | pt -i "Split firstname and lastname" -i "remove the address"
\n\n
{"first_name": "Jay", "last_name": "Neal"}
"""
