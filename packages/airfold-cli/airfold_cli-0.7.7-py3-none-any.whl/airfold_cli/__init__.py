from airfold_cli.root import app

# Import CLI submodules to register them to the app
# isort: split
import airfold_cli.config
import airfold_cli.diff
import airfold_cli.doctor
import airfold_cli.fmt
import airfold_cli.generate
import airfold_cli.graph
import airfold_cli.pipe
import airfold_cli.pull
import airfold_cli.push
import airfold_cli.source
