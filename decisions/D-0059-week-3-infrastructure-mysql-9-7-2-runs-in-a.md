# D-0059 — Week-3 infrastructure: MySQL 9.7.2 runs in a Docker container (image mysql:9.7, the LTS line) on every laptop, Docker Desktop installed before Mon 2026-10-26, the mysql client used through docker exec, Python reaches it through mysql-connector-python 26.7.0 from W3D3 on; the week-3 curriculum note and the thread domain name the container

- Date: 2026-10-16
- Status: accepted
- Decision: Week-3 infrastructure: MySQL 9.7.2 runs in a Docker container (image mysql:9.7, the LTS line) on every laptop, Docker Desktop installed before Mon 2026-10-26, the mysql client used through docker exec, Python reaches it through mysql-connector-python 26.7.0 from W3D3 on; the week-3 curriculum note and the thread domain name the container
- Why: Trainer decision 2026-10-16: MySQL runs inside Docker containers rather than a native install, so every laptop runs the same server version and a broken database is one docker rm away. Docker Hub on 2026-10-12: tag lts resolves to 9.7.2, latest and innovation to 26.7.0, 8.4.11 is still published; 9.7 is the current LTS line and the trainer chose it. Nothing in the curriculum, config or decisions mentioned Docker, and week 3 had no binding week note, so the week-3 plan author would have had nothing to go on. D-0048 applies: learners know no Docker, W3D1 teaches image, container, volume and port from first principles in its setup step.
- Affects: harness/curriculum.json week 3 notes (new), harness/config.json threads.p0-ticket-desk.domain (week-3 clause), harness/critics/research.md item 12 example, STATUS.md (new open item O-21: Docker Desktop on every laptop before Monday; trainer rehearsal of the pull and the connector install before the week-3 batch), harness/plans/week-03.md Run prerequisites (when written)
- Supersedes: —
- Superseded-by: —

## Notes

Container convention for the plan author: docker run --name desk-mysql -e MYSQL_ROOT_PASSWORD=... -p 3306:3306 -v desk-data:/var/lib/mysql -d mysql:9.7; client: docker exec -it desk-mysql mysql -uroot -p. Mon-Tue are SQL in the client; Wed-Fri alternate SQL and the Python desk. The demos critic runs every block's commit, so the container must be up on the trainer machine when demo-series.js runs.
