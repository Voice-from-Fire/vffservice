import {
    Button,
    Form,
    FormControl,
    FormGroup
} from "react-bootstrap";

import React, { useState } from 'react';
import { Body_login_auth_token_post, OpenAPI, SamplesService, UsersService } from "../generated/api";


interface LoginState {
    username: string,
    password: string,
}


export const Login = () => {
    const [state, setState] = useState<LoginState>({ username: "testuser", password: "pass" });

    return <div>
        <Form onSubmit={(e) => { e.preventDefault(); doLogin(state); }}>
            <Form.Group className="mb-3" controlId="formUsername">
                <Form.Label>Username</Form.Label>
                <Form.Control placeholder="Username"
                              value={state.username}
                              onChange={(e) => setState({ ...state, username: e.target.value})} />
            </Form.Group>

            <Form.Group className="mb-3" controlId="formBasicPassword">
                <Form.Label>Password</Form.Label>
                <Form.Control type="password"
                              placeholder="Password"
                              value={state.username}
                              onChange={(e) => setState({...state, password: e.target.value})}/>
            </Form.Group>
            <Button variant="primary" type="submit">
                Login
            </Button>
        </Form>
    </div>;
}

async function doLogin(user: LoginState) {
    let data: Body_login_auth_token_post = {
        username: user.username,
        password: user.password
      }
      OpenAPI.BASE = "http://localhost:8000"
      let r = await UsersService.loginAuthTokenPost(data)
      console.log(r);
      OpenAPI.TOKEN = r.access_token;
      let r2 = await SamplesService.getOwnSamplesSamplesGet();
      console.log(r2);
}