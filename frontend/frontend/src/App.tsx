import './App.css';
import { BrowserRouter as Router, Route, Switch } from 'react-router-dom';
import React, { Suspense, lazy } from 'react';

const HomePage = lazy(() => import('./homepage/components/HomePage/HomePage'));
const RedOrBlack = lazy(() => import('./redorblack/components/Game/game'));
const HighOrLow = lazy(() => import('./highorlow/components/Game/game'));

const App: React.FC = () => {
  return (
    <Router>
      <Suspense fallback={<div>Loading...</div>}>
        <Switch>
          <Route exact path="/" component={HomePage} />
          <Route exact path="/redorblack" component={RedOrBlack} />
          <Route exect path="/highorlow" component={HighOrLow} />
        </Switch>
      </Suspense>
    </Router>
  );
}

export default App;
