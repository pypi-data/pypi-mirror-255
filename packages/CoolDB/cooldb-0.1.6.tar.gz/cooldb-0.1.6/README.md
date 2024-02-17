<h1 align="center">CoolDB</h1>
<h3 align="center">CoolDB - это модуль для удобного использования баз данных на основе sqlite3 - для синхронного и асинхронного взаимодействия с базами данных.</h3>
<h1></h1>


<h4>SyncDataBaseRequests - это надстройка над sqlite3, призванная ускорить работу с базами данных sqlite в синхронном режиме.</h4>

> <h5>Пример синхронного использования</h5>
> Прелесть синхронного режима функций в том, что мы можем вызывать их, как в синхронном режиме, так и в асинхронном из кроутин, либо блокируя их действие, либо прокидывая их в асинхронный режим, по средствам asyncio.to_thread().
> И все таки более предпочтительным будет использовать асинхнонные варианты функций, чтобы попросту экономить мощности.



```python3

from CoolDB.SyncDataBaseRequests import RegRequests



def main():
	if RegRequests.get_db(
		dataBase="path/filename",
		table_name="your_table_name",
		columns="(name TEXT, age INTEGER, sex TEXT)"
	) is False:
		return 1

	if RegRequetsts.insert_to_db(
		dataBase="path/filename",
		table_name="your_table_name",
		parameters=["Игорь", 41, "Боевой вертолет СУ-34"]
	) is False:
		return 1

	print(RegRequests.fetch_all(
			dataBase="path/filename",
			table_name="your_table_name"
		))



if __name__ == "__main__":
	main()

```

<h1></h1>



<h4>AsyncDataBaseRequests - это надстройка над aiosqlite, призванная ускорить работу с базами данных sqlite в асинхронном режиме.</h4>

> <h5>Пример асинхронного использования</h5>
> При асинхронном режиме все точно также, только функции вызываются из кроутин.



```python3

import asyncio
from CoolDB.AsyncDataBaseRequests import RegRequests



async def main():
	if await RegRequests.get_db(
		dataBase="path/filename",
		table_name="your_table_name",
		columns="(name TEXT, age INTEGER, sex TEXT)"
	) is False:
		return 1

	if await RegRequetsts.insert_to_db(
		dataBase="path/filename",
		table_name="your_table_name",
		parameters=["Игорь", 41, "Боевой вертолет СУ-34"]
	) is False:
		return 1

	print(await RegRequests.fetch_all(
			dataBase="path/filename",
			table_name="your_table_name"
		))



if __name__ == "__main__":
	asyncio.run(main())

```
<h1></h1>



<h4>Разница между синхронном и асинхронным режимами в импортруемых модулях и в том, что в асинхронном режими функции вызываются из кроутин с добавлением ключевого слова await.</h4>
<h1></h1>



<h3 align="center">Документация</h3>
<h6 align="center">В CoolDB собраны регулярные функции взаимодействия с базами данных и помещены в класс RegRequest модуля SyncDataBaseRequests или AsyncDataBaseRequests:</h6>
<h1></h1>





<h5 align="center">Функция get_db()</h5>
<h6 align="center">Функция get_db() используется для создания таблицы в базе данных, если такой еще не существует. Попутно создает и базу данных, если ее еще не существует.</h6>


```python3

get_db(dataBase: str, table_name: str, columns: str) -> bool


```

Функция get_db() принимает три аргумента:

1. dataBase - путь до файла базы данных. Должен передаваться в формате строки формата: "path/filename".
> <h5>Примечания</h5>
> Предпочтительно хранить файл базы данных не глубже одной поддиректории от main файла

2. table_name - название таблицы в базе данных. Должен передаваться в формате строки.

3. columns - столбцы, с которыми необходимо будет создать базу данных, если она еще не была создана. Должны передаваться в формате строки формата: "(SQL_VARS)".
> <h5>Пример</h5>
> parameters = "(name TEXT, age INTEGER, sex TEXT)"

Пример использования:

```python3

if RegRequests.get_db(
	dataBase="path/filename",
	table_name="your_table_name",
	columns="(name TEXT, age INTEGER, sex TEXT)"
) is False:
	return 1

```
> <h5>Примечания</h5>
> В асинхронном режиме должна вызываться из кроутины и должно присутствовать ключевое слово await.
<h1></h1>





<h5 align="center">Функция insert_to_db()</h5>
<h6 align="center">Функция insert_to_db() используется для добавления элементов во все столбцы таблицы. Попутно создает и базу данных, если ее еще не существует.</h6>


```python3

insert_to_db(dataBase: str, table_name: str, parameters: list) -> bool


```

Функция insert_to_db() принимает три аргумента:

1. dataBase - путь до файла базы данных. Должен передаваться в формате строки формата: "path/filename".
> <h5>Примечания</h5>
> Предпочтительно хранить файл базы данных не глубже одной поддиректории от main файла

2. table_name - название таблицы в базе данных. Должен передаваться в формате строки.

3. parameters - параметры, которые необходимо будет поместить в базу данных. Должны передаваться в формате списка из переменных или значений.


Пример использования:

```python3

if RegRequests.insert_to_db(
	dataBase="path/filename",
	table_name="your_table_name",
	parameters=[X, Y, N, 42]
) is False:
	return 1

```
> <h5>Примечания</h5>
> insert_to_db() записывает значения во все существующие столбцы, поэтому количество передаваемых параметров, должно быть равным количеству существующих столбцов.
> В асинхронном режиме должна вызываться из кроутины и должно присутствовать ключевое слово await.
<h1></h1>





<h5 align="center">Функция insert_to_db_one_par()</h5>
<h6 align="center">Функция insert_to_db_one_par() используется для добавления элемента или элементов в определенный столбец или столбцы таблицы. Попутно создает и базу данных, если ее еще не существует.</h6>


```python3

insert_to_db_one_par(dataBase: str, table_name: str, column_name: str, parameter: str) -> bool


```

Функция insert_to_db_one_par() принимает четыре аргумента:

1. dataBase - путь до файла базы данных. Должен передаваться в формате строки формата: "path/filename".
> <h5>Примечания</h5>
> Предпочтительно хранить файл базы данных не глубже одной поддиректории от main файла

2. table_name - название таблицы в базе данных. Должен передаваться в формате строки.

3. column_name - названия столбца или столбцов, куда необходимо записать значения. Названия столбцов должны передаваться списком из названий в формате строки.

4. parameter - параметр, который необходимо будет поместить в базу данных или несколько параметров для определенных столбцов. Должны передаваться в формате строки формата "'X', 'Y', 'N'".


Пример использования:

```python3

if RegRequests.insert_to_db_one_par(
	dataBase="path/filename",
	table_name="your_table_name",
	column_name="forX, forY, forN"
	parameter="'X', 'Y', 'N'"
) is False:
	return 1

```
> <h5>Примечания</h5>
> В асинхронном режиме должна вызываться из кроутины и должно присутствовать ключевое слово await.
<h1></h1>





<h5 align="center">Функция fetch_all_where()</h5>
<h6 align="center">Функция fetch_all_where() используется для извлечения элементов из всех столбцов всех строк, в которых параметр поиска равен значению параметра поиска - условно, извлечь все столбцы всех строк, где айди=13.</h6>


```python3

fetch_all_where(dataBase: str, table_name: str, condition: str, condition_value: str | int) -> list[dict] | None


```

Функция fetch_all_where() принимает четыре аргумента:

1. dataBase - путь до файла базы данных. Должен передаваться в формате строки формата: "path/filename".
> <h5>Примечания</h5>
> Предпочтительно хранить файл базы данных не глубже одной поддиректории от main файла

2. table_name - название таблицы в базе данных. Должен передаваться в формате строки.

3. condition - параметер, по которому будет производится поиск в таблице.

4. condition_value - значение параметра, по которому будет производится поиск в таблице.


Пример использования:

```python3

if RegRequests.fetch_all_where(
	dataBase="path/filename",
	table_name="your_table_name",
	condition="id_",
	condition_value="121212"
) is None:
	return 1

```
> <h5>Примечания</h5>
> В асинхронном режиме должна вызываться из кроутины и должно присутствовать ключевое слово await.
<h1></h1>





<h5 align="center">Функция fetch_all()</h5>
<h6 align="center">Функция fetch_all() используется для извлечения всех элементов таблицы.</h6>


```python3

fetch_all(dataBase: str, table_name: str) -> list[dict] | None


```

Функция fetch_all() принимает два аргумента:

1. dataBase - путь до файла базы данных. Должен передаваться в формате строки формата: "path/filename".
> <h5>Примечания</h5>
> Предпочтительно хранить файл базы данных не глубже одной поддиректории от main файла

2. table_name - название таблицы в базе данных. Должен передаваться в формате строки.


Пример использования:

```python3

if RegRequests.fetch_all(
	dataBase="path/filename",
	table_name="your_table_name"
) is None:
	return 1

```
> <h5>Примечания</h5>
> В асинхронном режиме должна вызываться из кроутины и должно присутствовать ключевое слово await.
<h1></h1>





<h5 align="center">Функция fetch_one()</h5>
<h6 align="center">Функция fetch_one() используется для извлечения одного элемента таблицы.</h6>



```python3

fetch_one(dataBase: str, table_name: str, column_name: str, condition: str, condition_value: str | int) -> str | None


```

Функция fetch_one() принимает пять аргументов:

1. dataBase - путь до файла базы данных. Должен передаваться в формате строки формата: "path/filename".
> <h5>Примечания</h5>
> Предпочтительно хранить файл базы данных не глубже одной поддиректории от main файла

2. table_name - название таблицы в базе данных. Должен передаваться в формате строки.

3. column_name - названия столбца, откуда необходимо извлечь значение.

4. condition - параметер, по которому будет производится поиск в таблице.

5. condition_value - значение параметра, по которому будет производится поиск в таблице.


Пример использования:

```python3

if RegRequests.fetch_one(
	dataBase="path/filename",
	table_name="your_table_name",
	column_name="XYN",
	condition="id_",
	condition_value="121212"
) is None:
	return 1

```
> <h5>Примечания</h5>
> В асинхронном режиме должна вызываться из кроутины и должно присутствовать ключевое слово await.
<h1></h1>





<h5 align="center">Функция exists_test()</h5>
<h6 align="center">Функция exists_test() используется для проверки существования таблицы.</h6>


```python3

exists_test(dataBase: str, table_name: str) -> bool


```

Функция exists_test() принимает два аргумента:

1. dataBase - путь до файла базы данных. Должен передаваться в формате строки формата: "path/filename".
> <h5>Примечания</h5>
> Предпочтительно хранить файл базы данных не глубже одной поддиректории от main файла

2. table_name - название таблицы в базе данных. Должен передаваться в формате строки.


Пример использования:

```python3

if RegRequests.exists_test(
	dataBase="path/filename",
	table_name="your_table_name"
) is False:
	return 1

```
> <h5>Примечания</h5>
> В асинхронном режиме должна вызываться из кроутины и должно присутствовать ключевое слово await.
<h1></h1>





<h5 align="center">Функция update_table()</h5>
<h6 align="center">Функция update_table() используется для обновления определенного элемента определенного столбца.</h6>



```python3

update_table(dataBase: str, table_name: str, column_name: str, new_meaning: str, condition: str, condition_value: str | int) -> bool


```

Функция update_table() принимает шесть аргументов:

1. dataBase - путь до файла базы данных. Должен передаваться в формате строки формата: "path/filename".
> <h5>Примечания</h5>
> Предпочтительно хранить файл базы данных не глубже одной поддиректории от main файла

2. table_name - название таблицы в базе данных. Должен передаваться в формате строки.

3. column_name - названия столбца, откуда необходимо извлечь значение.

4. new_meaning - новое значение выбранного столбца

5. condition - параметер, по которому будет производится поиск в таблице.

6. condition_value - значение параметра, по которому будет производится поиск в таблице.


Пример использования:

```python3

if RegRequests.update_table(
	dataBase="path/filename",
	table_name="your_table_name",
	column_name="XYN",
	new_meaning="URAURAURAURAURA"
	condition="id_",
	condition_value="121212"
) is None:
	return 1

```
> <h5>Примечания</h5>
> В асинхронном режиме должна вызываться из кроутины и должно присутствовать ключевое слово await.
<h1></h1>





<h5 align="center">Функция delete_from_table()</h5>
<h6 align="center">Функция delete_from_table() используется для удаления строки, в столбце которой есть совпадения с условием.</h6>


```python3

delete_from_table(dataBase: str, table_name: str, condition: str, condition_value: str | int) -> bool


```

Функция delete_from_table() принимает четыре аргумента:

1. dataBase - путь до файла базы данных. Должен передаваться в формате строки формата: "path/filename".
> <h5>Примечания</h5>
> Предпочтительно хранить файл базы данных не глубже одной поддиректории от main файла

2. table_name - название таблицы в базе данных. Должен передаваться в формате строки.

3. condition - параметер, по которому будет производится поиск в таблице.

4. condition_value - значение параметра, по которому будет производится поиск в таблице.


Пример использования:

```python3

if RegRequests.delete_from_table(
	dataBase="path/filename",
	table_name="your_table_name",
	condition="id_",
	condition_value="121212"
) is False:
	return 1

```
> <h5>Примечания</h5>
> В асинхронном режиме должна вызываться из кроутины и должно присутствовать ключевое слово await.
<h1></h1>





<h5 align="center">Функция delete_table()</h5>
<h6 align="center">Функция delete_table() используется для удаления всех таблицы избазы данных.</h6>


```python3

delete_table(dataBase: str, table_name: str) -> bool


```

Функция delete_table() принимает два аргумента:

1. dataBase - путь до файла базы данных. Должен передаваться в формате строки формата: "path/filename".
> <h5>Примечания</h5>
> Предпочтительно хранить файл базы данных не глубже одной поддиректории от main файла

2. table_name - название таблицы в базе данных. Должен передаваться в формате строки.


Пример использования:

```python3

if RegRequests.delete_table(
	dataBase="path/filename",
	table_name="your_table_name"
) is False:
	return 1

```
> <h5>Примечания</h5>
> В асинхронном режиме должна вызываться из кроутины и должно присутствовать ключевое слово await.
<h1></h1>


