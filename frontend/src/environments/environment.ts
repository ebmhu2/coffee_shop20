/* @TODO replace with your variables
 * ensure all variables on this page match your project
 */

export const environment = {
  production: false,
  apiServerUrl: 'http://127.0.0.1:5000', // the running FLASK api server url
  auth0: {
    url: 'udacity2020.eu', // the auth0 domain prefix
    audience: 'coffee_shop_api', // the audience set for the auth0 app
    clientId: 'XzfZoHMGLBsS6YoHQq9MJYu56QwhA49o', // the client id generated for the auth0 app
    callbackURL: 'http://127.0.0.1:8100/callback', // the base url of the running ionic application.
  }
};
