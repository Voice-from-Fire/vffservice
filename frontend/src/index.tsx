import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';
import reportWebVitals from './reportWebVitals';
import { OpenAPI, UsersService, SamplesService, Body_login_auth_token_post } from './generated/api';

import 'bootstrap/dist/css/bootstrap.min.css';
import { BrowserRouter } from 'react-router-dom';

const root = ReactDOM.createRoot(
  document.getElementById('root') as HTMLElement
);
root.render(
  <React.StrictMode>
    <BrowserRouter>
      <App />
    </BrowserRouter>
  </React.StrictMode>
);

async function login() {
  let data: Body_login_auth_token_post = {
    username: "abc",
    password: "cde"
  }
  OpenAPI.BASE = "http://localhost:8000"
  let r = await UsersService.loginAuthTokenPost(data)
  console.log(r);
  OpenAPI.TOKEN = r.access_token;
  let r2 = await SamplesService.getOwnSamplesSamplesGet();
  console.log(r2);
}

login()

// If you want to start measuring performance in your app, pass a function
// to log results (for example: reportWebVitals(console.log))
// or send to an analytics endpoint. Learn more: https://bit.ly/CRA-vitals
reportWebVitals();
