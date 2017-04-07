var React = require('react');

class Index extends React.Component{
  constructor(props) {
    super(props);
  }

  render() {
    const django = 'django';
    console.log(django)

    return (
      <div>
        <div>Hello django-react!</div>
      </div>  
    )
  }
}

module.exports = Index;
