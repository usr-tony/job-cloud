import React from "react";
import { RenderTable, database } from './table'
import ReactDOM from 'react-dom'

const defaultState = () => ({
    index: 0,
    get title() { return database[this.index].title },
    get name() { return database[this.index].name }
})

function Lastupdate(props) {
    let seconds = Date.now() / 1000 - props.time
    let hours = Math.floor(seconds / 3600)
    let minutes = Math.floor(seconds % 3600 / 60)
    let text = ''
	if (hours > 1) {
		text += hours + ' hours'
	} else if (hours == 1) {
		text += '1 hour';
	}
	if (text != ''){
		text += ' and '
	}
	if (minutes > 1){
		text += minutes + ' minutes ago'
	} else if (minutes == 1){
		text += '1 minute ago'
	} else if (text == ''){
		text += 'just now'
	} else {
		text += 'ago'
	}
    return (
        <div>
            <p>
                Last updated {text}
            </p>
            <p>
                updates every 12 hours
            </p>
        </div>
    )
}
class App extends React.Component {
    constructor(props) {
        super(props)
        this.state = defaultState()
    }
    clickHandler = (event) => {
        let index = event.target.id
        this.setState(() => ({
            index: index,
            title: database[index].title,
            name: database[index].name
        }))
        RenderTable(event.target.id)
    }
    render() {
        let buttons = []
        for (let i in [...Array(database.length).keys()]) {
            buttons.push(
                <button className="btn btn-info" onClick={this.clickHandler} id={i} key={i} style={{ marginBottom: '12%' }}>
                    {database[i].name}
                </button>
            )
        }
        return (
            <div className='d-flex container' style={{ alignItems: 'center', justifyContent: 'center', height: '90vh' }}>
                <div className=' d-flex flex-column' style={{ marginRight: '5%' }}>
                    <h4 className='m-3' style={{ 'textAlign': 'center' }}>
                        {this.state.title}
                    </h4>
                    <div id="table"></div>
                </div>
                <div className=' d-flex flex-column m-2'>
                    <div className="d-flex flex-column">
                        {buttons.map(button => button)}
                    </div>
                    <Lastupdate time={database[0].time} />
                    <div id='introduction section' className='mt-5'>
                        <p>
                            Created with React.js, D3.js, Python(backend).
                            <br />
                            Hosted on Amazon Web Services, data stored on
                            <br />
                            RDS, hosted on an EC2 instance.
                        </p>
                    </div>
                </div>
            </div>
        )
    }
}

ReactDOM.render(<App />, document.querySelector('#app'))
RenderTable(0)
