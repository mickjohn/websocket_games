import React from 'react';
import ReactDOM from 'react-dom';
import ConnStatus from './conn_status';


it('renders without crashing', () => {
  const div = document.createElement('div');
  ReactDOM.render(<ConnStatus status={123} />, div);
  ReactDOM.unmountComponentAtNode(div);
});
