## Sample SQL queries using the SQLite CLI

Connect to the database cases.db in the terminal using the sqlite3 cli:

```bash
.../wa-opinions/data$ sqlite3 cases.db
```

#### Find all attorneys whose name contains a string (e.g. "Smith"):

```sql
SELECT *
FROM attorneys
WHERE name LIKE '%Smith%';
```
> [!TIP]
> SQLite is case-insensitive by default for ASCII. Use LOWER if need case-insensitive search across all Unicode:

```sql
SELECT *
FROM attorneys
WHERE LOWER(name) LIKE LOWER('%Smith%');
```

#### Get list of unique attorney, judge, litigant names:

```sql
SELECT DISTINCT name
FROM attorneys
ORDER BY name;

SELECT DISTINCT name
FROM judges
ORDER BY name;

SELECT DISTINCT name
FROM litigants
ORDER BY name;
```

#### See how many cases an attorney or judge appears in:

```sql
SELECT name, COUNT(*) AS appearances
FROM attorneys
GROUP BY name
ORDER BY appearances DESC;

SELECT name, COUNT(*) AS appearances
FROM judges
GROUP BY name
ORDER BY appearances DESC;
```

#### Join attorneys table to cases to see all cases an attorney is associated with:

```sql
SELECT c.id,
       c.case_title,
       c.panel_date,
       c.division
FROM cases c
JOIN attorneys a ON c.id = a.case_id
WHERE a.name = 'Aric Hamilton Jarrett'
ORDER BY c.panel_date;
```

#### Include the case numbers for the query above

```sql
SELECT
    GROUP_CONCAT(cn.case_number, ', ') AS case_numbers,
    c.case_title,
    c.panel_date,
    a.name AS attorney_name
FROM attorneys a
JOIN cases c ON c.id = a.case_id
LEFT JOIN case_numbers cn ON cn.case_id = c.id
GROUP BY
    c.id,
    a.id
ORDER BY
    attorney_name,
    c.panel_date;
```

#### Run a SQL query in the Sqlite3 CLI and save the output to a csv file:

```sql
.headers on
.mode csv
.output output_filename.csv
[SQL QUERY]
.output stdout
```

> [!TIP]
> To filter the query above on a specific attorney, add a where clause:

```sql
WHERE a.name = 'Jane Doe'
```

