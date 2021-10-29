# Deployment

Deployment is automated through github actions, see more information in the README.

This repository deploys to 3 environments:

* The `main` branch deploys to the `dit` environment.
* The `staging` branch deploys to the `staging` environment.
* The `production` branch deploys to the `producion` environment.

The API Gateway endpoint can be viewable as output in the Github Actions interface.

Pushing to staging and production is maintained by owners of this repository and should follow these steps:

## 1. Merge the `production` branch into the `main` branch and test the DIT environment.

Merge the `production` branch into the `main` branch to make sure that there aren't any (possibly conflicting) changes.

```bash
git checkout production
git pull origin production
git checkout main
git pull origin main
git merge production
git push origin main
```

If there are no differences you should see:

```bash
git:(main) git merge production
Already up to date.
git:(main) git push origin main
Everything up-to-date
```

Test the dit environment if differences were merged in from production.

## 2. Create a release branch and add to the CHANGELOG

```bash
export TAG=v1.0.0
git checkout -b $TAG
```

Compare this branch with previous release and add notable changes to the CHANGELOG.md.

```
git commit -am "Add release changes to CHANGELOG.md"
```

Open a PR and merge to main once approved.

## 3. Push the tag, push and test staging and production

Now that main has the CHANGELOG updates, create a relase tag and promote those changes.

```bash
git checkout $TAG
git pull origin $TAG
git tag -a $TAG -m "Release ${TAG}"
git push origin $TAG
```

Test the DIT environment (biomass.dit.maap-project.org)

### Checkout and push to staging

```bash
git co staging
git pull staging
git merge -s theirs staging
git push origin $TAG
```

### Checkout and push to production

```bash
git co production
git pull production
git merge -s theirs production
git push origin $TAG
```