# Publication Data and Figures

### Description
The files in this directory generate all figures and statistics presented in the publication manuscript.  The subdirectories in this directory contain the figures/statistics or other input data required to generate them.

### Files
- **performance_comparison.py** loads data from the `pandemic-central/output/ReichLabFormat/publication/` directory and the `data/comparison_models/` subdirectory to generate statistics on their relative performance.  These statistics are stored in the `output/model_performance/` subdirectory.
- **performance_graph.py** produces graphs of the statistics from `performance_comparison.py`.  These graphs are stored in the `output/performance_figures/` subdirectory.
- **feature_importance.py** produces graphs of computed feature importances over time from datasets in the `pandemic-central/output/feature_ranking/publication/` directory. The output graphs are in the `output/feature_importance_figures/` subdirectory.
- **rt_alignment.py** graphs an example of the R<sub>t</sub> alignment process with the case curves, producing the figure in the `output/rt_alignment_figures/` subdirectory.
- **misc_stats.py** prints statistics referenced in the publication manuscript Results and Discussion section.

### Subdirectories
- `data/` contains projections from other models in the `data/comparison_models/` subdirectory and the **higher_corrs.csv** file originally found in the `pandemic-central/data/Rt/` directory, but computed for 2021-01-10 projections.
- `output/` contains output figures and datasets from the code files in this directory as described in the section directly above on Files in this directory.
