.PHONY: install
.PHONY: upgrade-pollination-react
.PHONY: generate-frontend

upgrade-pollination-react:
	npm i pollination-react-io@latest --prefix pollination_streamlit_io/components/frontend 

generate-frontend:
	npm run build --prefix pollination_streamlit_io/components/frontend 

install: 
	npm i --force --package-lock-only --prefix pollination_streamlit_io/components/frontend
