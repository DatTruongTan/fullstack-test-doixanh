import { useState, useEffect } from 'react';
import { taskAPI } from '../api';
import type { Task, TaskCreate } from '../types';
import { useToast } from '../contexts/ToastContext';
import TaskItem from './TaskItem';
import AddTaskForm from './AddTaskForm';

const isSessionExpiredError = (err: any): boolean => {
    return err?.response?.status === 401;
};

const TaskList = () => {
    const [tasks, setTasks] = useState<Task[]>([]);
    const [loading, setLoading] = useState(true);
    const [searchQuery, setSearchQuery] = useState('');
    const [showCompleted, setShowCompleted] = useState(true);
    const [selectedTasks, setSelectedTasks] = useState<number[]>([]);
    const [showBulkActions, setShowBulkActions] = useState(false);

    const { addToast } = useToast();

    useEffect(() => {
        fetchTasks();
    }, []);

    useEffect(() => {
        setShowBulkActions(selectedTasks.length > 0);
    }, [selectedTasks]);

    const fetchTasks = async () => {
        try {
            setLoading(true);
            const data = await taskAPI.getTasks();
            const sortedTasks = [...data].sort((a, b) =>
                new Date(a.due_date).getTime() - new Date(b.due_date).getTime()
            );
            setTasks(sortedTasks);
        } catch (err) {
            console.error(err);
            if (!isSessionExpiredError(err)) {
                addToast('Failed to load tasks. Please try again.', 'error');
            }
        } finally {
            setLoading(false);
        }
    };

    const handleSearch = async () => {
        if (!searchQuery.trim()) {
            fetchTasks();
            return;
        }

        try {
            setLoading(true);
            const data = await taskAPI.searchTasks(searchQuery);
            const sortedTasks = [...data].sort((a, b) =>
                new Date(a.due_date).getTime() - new Date(b.due_date).getTime()
            );
            setTasks(sortedTasks);
        } catch (err) {
            console.error(err);
            if (!isSessionExpiredError(err)) {
                addToast('Failed to search tasks. Please try again.', 'error');
            }
        } finally {
            setLoading(false);
        }
    };

    const handleAddTask = async (taskData: TaskCreate) => {
        try {
            const newTask = await taskAPI.createTask(taskData);
            const updatedTasks = [...tasks, newTask];
            const sortedTasks = updatedTasks.sort((a, b) =>
                new Date(a.due_date).getTime() - new Date(b.due_date).getTime()
            );
            setTasks(sortedTasks);
            addToast('Task added successfully!', 'success');
            return true;
        } catch (err) {
            console.error(err);
            if (!isSessionExpiredError(err)) {
                addToast('Failed to add task. Please try again.', 'error');
            }
            return false;
        }
    };

    const handleUpdateTask = async (
        id: number,
        updates: {
            title?: string;
            description?: string;
            completed?: boolean;
            due_date?: string;
            priority?: 'low' | 'normal' | 'high';
        }
    ) => {
        try {
            const task = tasks.find((t) => t.id === id);
            if (!task) return false;

            const updatedTask = await taskAPI.updateTask(id, {
                ...task,
                ...updates,
            });

            const updatedTasks = tasks.map((t) => (t.id === id ? updatedTask : t));
            const sortedTasks = updatedTasks.sort((a, b) =>
                new Date(a.due_date).getTime() - new Date(b.due_date).getTime()
            );
            setTasks(sortedTasks);

            if (!('completed' in updates && Object.keys(updates).length === 1)) {
                addToast('Task updated successfully!', 'success');
            }
            return true;
        } catch (err) {
            console.error(err);
            if (!isSessionExpiredError(err)) {
                addToast('Failed to update task. Please try again.', 'error');
            }
            return false;
        }
    };

    const handleDeleteTask = async (id: number) => {
        try {
            await taskAPI.deleteTask(id);
            setTasks(tasks.filter((task) => task.id !== id));
            if (selectedTasks.includes(id)) {
                setSelectedTasks(selectedTasks.filter((taskId) => taskId !== id));
            }
            addToast('Task removed successfully!', 'success');
            return true;
        } catch (err) {
            console.error(err);
            if (!isSessionExpiredError(err)) {
                addToast('Failed to delete task. Please try again.', 'error');
            }
            return false;
        }
    };

    const handleTaskSelection = (id: number, isSelected: boolean) => {
        if (isSelected) {
            setSelectedTasks([...selectedTasks, id]);
        } else {
            setSelectedTasks(selectedTasks.filter((taskId) => taskId !== id));
        }
    };

    const handleBulkDelete = async () => {
        try {
            setLoading(true);
            for (const taskId of selectedTasks) {
                await taskAPI.deleteTask(taskId);
            }
            setTasks(tasks.filter((task) => !selectedTasks.includes(task.id)));
            addToast(`${selectedTasks.length} tasks removed successfully!`, 'success');
            setSelectedTasks([]);
            return true;
        } catch (err) {
            console.error(err);
            if (!isSessionExpiredError(err)) {
                addToast('Failed to delete tasks. Please try again.', 'error');
            }
            return false;
        } finally {
            setLoading(false);
        }
    };

    const filteredTasks = showCompleted
        ? tasks
        : tasks.filter((task) => !task.completed);

    return (
        <div className="task-list-container">
            <div className="add-task-column">
                <AddTaskForm onAddTask={handleAddTask} />
            </div>

            <div className="task-list-column">
                <div className="task-controls">
                    <div className="search-box">
                        <input
                            type="text"
                            value={searchQuery}
                            onChange={(e) => setSearchQuery(e.target.value)}
                            placeholder="Search tasks..."
                        />
                        <button onClick={handleSearch}>Search</button>
                        {searchQuery && (
                            <button onClick={() => { setSearchQuery(''); fetchTasks(); }}>
                                Clear
                            </button>
                        )}
                    </div>

                    <div className="filter-controls">
                        <label className="show-completed-label">
                            <input
                                type="checkbox"
                                checked={showCompleted}
                                onChange={(e) => setShowCompleted(e.target.checked)}
                            />
                            Show Completed
                        </label>
                    </div>
                </div>

                {showBulkActions && (
                    <div className="bulk-actions">
                        <span>{selectedTasks.length} tasks selected</span>
                        <div className="bulk-action-buttons">
                            <button onClick={handleBulkDelete}>Remove Selected</button>
                        </div>
                    </div>
                )}

                {loading ? (
                    <div className="loading">Loading tasks...</div>
                ) : filteredTasks.length > 0 ? (
                    <div className="task-list">
                        {filteredTasks.map((task) => (
                            <TaskItem
                                key={task.id}
                                task={task}
                                onDelete={handleDeleteTask}
                                onUpdate={handleUpdateTask}
                                onCheckboxChange={handleTaskSelection}
                                isSelected={selectedTasks.includes(task.id)}
                            />
                        ))}
                    </div>
                ) : (
                    <div className="empty-list">No tasks found</div>
                )}
            </div>
        </div>
    );
};

export default TaskList; 