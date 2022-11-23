import React from 'react';
import logo from './logo.svg';
import './App.css';
import { Button, Container, Nav, Navbar, Stack } from 'react-bootstrap';

function App() {
  return (
    <div className="App">
      <Navbar bg="dark" variant="dark">
        <Container>
          <Navbar.Brand href="#home">VoiceFromFire</Navbar.Brand>
          <Nav className="me-auto">
            <Nav.Link href="#samples">My samples</Nav.Link>
            <Nav.Link href="#labels">Label others</Nav.Link>
            <Nav.Link href="#docs">Documentation</Nav.Link>
          </Nav>
        </Container>
      </Navbar>
      <br />
    </div>
  );
}

export default App;
