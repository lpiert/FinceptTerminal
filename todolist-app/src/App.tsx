import { useState, useEffect } from 'react'
import './App.css'

interface Todo {
  id: number
  text: string
  completed: boolean
  createdAt: Date
}

function App() {
  const [todos, setTodos] = useState<Todo[]>([])
  const [inputValue, setInputValue] = useState('')
  const [filter, setFilter] = useState<'all' | 'active' | 'completed'>('all')

  // Load todos from localStorage on mount
  useEffect(() => {
    const savedTodos = localStorage.getItem('todos')
    if (savedTodos) {
      const parsed = JSON.parse(savedTodos)
      // Convert date strings back to Date objects
      const todosWithDates = parsed.map((todo: any) => ({
        ...todo,
        createdAt: new Date(todo.createdAt)
      }))
      setTodos(todosWithDates)
    }
  }, [])

  // Save todos to localStorage whenever they change
  useEffect(() => {
    localStorage.setItem('todos', JSON.stringify(todos))
  }, [todos])

  const addTodo = () => {
    if (inputValue.trim() === '') return
    
    const newTodo: Todo = {
      id: Date.now(),
      text: inputValue.trim(),
      completed: false,
      createdAt: new Date()
    }
    
    setTodos([...todos, newTodo])
    setInputValue('')
  }

  const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      addTodo()
    }
  }

  const toggleTodo = (id: number) => {
    setTodos(todos.map(todo => 
      todo.id === id ? { ...todo, completed: !todo.completed } : todo
    ))
  }

  const deleteTodo = (id: number) => {
    setTodos(todos.filter(todo => todo.id !== id))
  }

  const clearCompleted = () => {
    setTodos(todos.filter(todo => !todo.completed))
  }

  const filteredTodos = todos.filter(todo => {
    if (filter === 'active') return !todo.completed
    if (filter === 'completed') return todo.completed
    return true
  })

  const activeTodosCount = todos.filter(todo => !todo.completed).length
  const completedTodosCount = todos.filter(todo => todo.completed).length

  return (
    <div className="app">
      <header className="app-header">
        <h1>📝 Todo List</h1>
        <p className="subtitle">Stay organized, get things done</p>
      </header>

      <div className="todo-container">
        {/* Input Section */}
        <div className="input-section">
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="What needs to be done?"
            className="todo-input"
          />
          <button onClick={addTodo} className="add-button">
            Add Task
          </button>
        </div>

        {/* Filter Tabs */}
        <div className="filter-section">
          <div className="filter-tabs">
            <button
              className={`filter-tab ${filter === 'all' ? 'active' : ''}`}
              onClick={() => setFilter('all')}
            >
              All ({todos.length})
            </button>
            <button
              className={`filter-tab ${filter === 'active' ? 'active' : ''}`}
              onClick={() => setFilter('active')}
            >
              Active ({activeTodosCount})
            </button>
            <button
              className={`filter-tab ${filter === 'completed' ? 'active' : ''}`}
              onClick={() => setFilter('completed')}
            >
              Completed ({completedTodosCount})
            </button>
          </div>
          {completedTodosCount > 0 && (
            <button onClick={clearCompleted} className="clear-button">
              Clear Completed
            </button>
          )}
        </div>

        {/* Todo List */}
        <div className="todo-list">
          {filteredTodos.length === 0 ? (
            <div className="empty-state">
              <span className="empty-icon">✨</span>
              <p>
                {filter === 'all' 
                  ? 'No tasks yet. Add your first task above!'
                  : filter === 'active'
                  ? 'No active tasks. Great job!'
                  : 'No completed tasks yet.'}
              </p>
            </div>
          ) : (
            filteredTodos.map(todo => (
              <div
                key={todo.id}
                className={`todo-item ${todo.completed ? 'completed' : ''}`}
              >
                <div className="todo-content">
                  <input
                    type="checkbox"
                    checked={todo.completed}
                    onChange={() => toggleTodo(todo.id)}
                    className="todo-checkbox"
                  />
                  <span className="todo-text">{todo.text}</span>
                </div>
                <button
                  onClick={() => deleteTodo(todo.id)}
                  className="delete-button"
                  title="Delete task"
                >
                  ×
                </button>
              </div>
            ))
          )}
        </div>

        {/* Footer Stats */}
        {todos.length > 0 && (
          <div className="todo-footer">
            <span>{activeTodosCount} item{activeTodosCount !== 1 ? 's' : ''} left</span>
            <span className="progress-bar">
              <div 
                className="progress-fill" 
                style={{ 
                  width: `${todos.length > 0 ? (completedTodosCount / todos.length) * 100 : 0}%` 
                }}
              />
            </span>
            <span>{Math.round((completedTodosCount / todos.length) * 100)}% complete</span>
          </div>
        )}
      </div>
    </div>
  )
}

export default App
