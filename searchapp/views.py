import MySQLdb
import os
from django.shortcuts import render
from .forms import MySQLConnectionForm

LOG_FILE = 'search_progress.log'

def log_progress(table, column, last_id=None, last_row=None):
    with open(LOG_FILE, 'a') as log_file:
        log_file.write(f"{table}:{column}:{last_id if last_id is not None else 'None'}:{last_row if last_row is not None else 'None'}\n")

def clear_log():
    if os.path.exists(LOG_FILE):
        os.remove(LOG_FILE)

def read_last_progress():
    if not os.path.exists(LOG_FILE):
        return None
    with open(LOG_FILE, 'r') as log_file:
        lines = log_file.readlines()
        if lines:
            last_line = lines[-1].strip()
            parts = last_line.split(':')
            table = parts[0]
            column = parts[1]
            last_id = int(parts[2]) if parts[2] != 'None' else None
            last_row = int(parts[3]) if parts[3] != 'None' else None
            return table, column, last_id, last_row
        return None

def is_integer_column(column_type):
    return column_type.upper() in ('INT', 'BIGINT', 'TINYINT')

def search_database(request):
    if request.method == 'POST':
        form = MySQLConnectionForm(request.POST)
        if form.is_valid():
            host = form.cleaned_data['host']
            database = form.cleaned_data['database']
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            search_text = form.cleaned_data['search_text']
            clear_log_flag = form.cleaned_data.get('clear_log', False)

            if clear_log_flag:
                clear_log()

            last_progress = read_last_progress()

            try:
                conn = MySQLdb.connect(
                    host=host,
                    user=username,
                    passwd=password,
                    db=database,
                    connect_timeout=5
                )
                cursor = conn.cursor()

                if last_progress:
                    table, column, last_id, last_row = last_progress
                    start_search = False
                else:
                    start_search = True
                    last_id = 0
                    last_row = 0

                results = {}
                cursor.execute("SHOW TABLES")
                tables = cursor.fetchall()

                for (table_name,) in tables:
                    if not start_search and table_name == table:
                        start_search = True
                    if start_search:
                        cursor.execute(f"SHOW COLUMNS FROM {table_name}")
                        columns = cursor.fetchall()

                        # Identify the primary key column (if any)
                        primary_key_column = None
                        primary_key_type = None
                        for column_info in columns:
                            if column_info[3] == 'PRI':  # 3rd index usually indicates if it's a primary key
                                primary_key_column = column_info[0]
                                primary_key_type = column_info[1]
                                break

                        row_number = 0

                        for column in columns:
                            column_name = column[0]
                            query = f"SELECT * FROM {table_name} WHERE `{column_name}` LIKE '%{search_text.replace(' ', '%')}%'"
                            
                            if primary_key_column and is_integer_column(primary_key_type) and last_id:
                                query += f" AND `{primary_key_column}` > {last_id}"

                            cursor.execute(query)
                            rows = cursor.fetchall()

                            for row in rows:
                                row_number += 1
                                if primary_key_column and is_integer_column(primary_key_type):
                                    last_id_in_row = row[next(i for i, col in enumerate(columns) if col[0] == primary_key_column)]
                                    log_progress(table_name, column_name, last_id=last_id_in_row, last_row=row_number)
                                else:
                                    log_progress(table_name, column_name, last_row=row_number)

                                if table_name not in results:
                                    results[table_name] = []
                                results[table_name].append(
                                    {
                                        'rows': [row],
                                        'columns': columns,
                                        'column_name': column_name
                                    }
                                )

                conn.close()
                return render(request, 'results.html', {'results': results, 'form': form,'tables':tables})
            
            except MySQLdb.Error as e:
                log_progress(f"Error: {str(e)}", "", 0)
                return render(request, 'search.html', {'form': form, 'error': str(e)})

    else:
        form = MySQLConnectionForm()

    return render(request, 'search.html', {'form': form})