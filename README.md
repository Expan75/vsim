# FFR120 - Voting simulator project

This repo contains the code for simulating voting systems as part of a class project for FFR120.

### Experiments

This matrix corresponds to the experiments were are planning to run and wether or not the simulator currently supports doing so. Completed means that results of simulation are captured in a version controlled notebook.

| voting system              | electorate scenario | dispersion     | supported                | completed analysis       |
| -------------------------- | ------------------- | -------------- | ------------------------ | ------------------------ |
| plurality                  | all                 | None, high     | <ul><li>- [x] </li></ul> | <ul><li>- [x] </li></ul> |
| majority                   | all                 | None, high     | <ul><li>- [x] </li></ul> | <ul><li>- [x] </li></ul> |
| ranked choice              | all                 | None, high     | <ul><li>- [x] </li></ul> | <ul><li>- [ ] </li></ul> |
| proportional, no threshold | all                 | None, high     | <ul><li>- [x] </li></ul> | <ul><li>- [ ] </li></ul> |
| proportional, 4% threshold | all                 | None, high     | <ul><li>- [x] </li></ul> | <ul><li>- [ ] </li></ul> |
| plurality                  | swedish public      | not applicable | <ul><li>- [ ] </li></ul> | <ul><li>- [ ] </li></ul> |
| majority                   | swedish public      | not applicable | <ul><li>- [ ] </li></ul> | <ul><li>- [ ] </li></ul> |
| ranked choice              | swedish public      | not applicable | <ul><li>- [ ] </li></ul> | <ul><li>- [ ] </li></ul> |

### Getting started with analysis

You can use the simulator to simulate and analyse different electoral systems. Checkout the **plurality_vs_majority.ipynb** notebook for a walkthrough. You can open it via jupyter notebook by running the command:

```bash
python3 -m jupyter notebook plurality_vs_majority.ipynb
```

### Getting started with development

If you are opting to help run the simulator, it is many times easier to run it via the command line. See below for how to do that.

```
# install dependencies
python3 -m pip install -r requirements.txt

# run the simulation for a given voting system, and visualise
python3 cli.py \
    --voting-system plurality \
    --scenario polarized \
    --candidates 2 \
    --population 10_000 \
    --debug \
    --log debug

# run with more settings, logging and graphical output
python3 cli.py \
    --voting-system majority \
    --candidates 5
    --population 10_000
```

Supported systems of voting are currently:

- plurality
- majority
- approval

### Contributing

To contribute, make a branch, commit and push your changes and then create a pull request to merge to the develop branch. Be sure to integrate the latest develop version into your branch.

1. Go to github and clone the code
2. Create a new branch

```bash
git checkout -B my-feature-branch
```

3. Add your changes

```
git add .
git commit -am "description of my changes"
git push -u origin my-feature-branch
```

4. Navigate to (GitHub)[https://github.com/Expan75/complex-simulation-project/pulls] and create a new pull request under the branch to merge into main.

5. Complete code review and your done!

### Testing parameters

Voting systems: plurality, majority, approval
Populaton size: 10 000, 100 000, 1 000 000, 10 000 000
Candidates: 2, 4, 6, 8
scenario: centered, random, polarized 2 cohorts, polarized 4 cohorts, polarized 6 cohorts, polarized 8 cohorts,
standard deviations, what is proper standard deviation?

### Future testing parameters

Voting apathy (to long distance --> no vote)

simulate the swedish parties from data in reasearch

strategic voting (vote nearest)
support voting (4% limit)

3 dimensional space? kinda easy to visualize and add another axis from CHES2019V3?
