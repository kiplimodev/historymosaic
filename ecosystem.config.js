module.exports = {
  apps : [{
    name: 'historical-events-autoposter',
    script: 'src/autopost.py',
    interpreter: 'python3',
    env: {
      NODE_ENV: 'development',
    },
    env_production: {
      NODE_ENV: 'production',
      ENVIRONMENT: 'production',
      X_DRY_RUN: 'false',
    }
  }]
};