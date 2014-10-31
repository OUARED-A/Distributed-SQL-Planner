SELECT employer,sum(salary) FROM dhs AS D GROUP BY employer HAVING sum(salary) > 1000
