.PHONY: gen-data apply train-retrieve materialize serve-lookup swap-redis test

gen-data:
	python scripts/gen_data.py

apply:
	cd feature_store && feast apply

train-retrieve:
	python scripts/train_retrieve.py

materialize:
	cd feature_store && feast materialize-incremental $$(date +%Y-%m-%d)

serve-lookup:
	python scripts/serve_lookup.py

swap-redis:
	docker run -d --name feast-redis -p 6379:6379 redis:7 || docker start feast-redis
	@echo "Now edit feature_store/feature_store.yaml online_store to redis, then: make apply materialize serve-lookup"

test:
	pytest -q
