python ../manage.py graph_models -a > models_diagram.dot
python ../manage.py graph_models -a -g -o models_diagram.png
python ../manage.py graph_models generator -o models_diagram_generator.png
python ../manage.py graph_models evaluator -o models_diagram_evaluator.png

