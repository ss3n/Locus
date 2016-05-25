This is a directory with all the database setup files. This README file serves as a repository of learnings and descriptions of various tables used in our system:

__Region Table__
  - id: INT
  - name: VARCHAR
  - rpolygon: POLYGON

Sample MySQL query for running a Point-in-Polygon operation:

`SELECT * FROM region where ST_Contains(rpolygon, ST_GeomFromText('Point(-117.841949 33.646201)'));`
