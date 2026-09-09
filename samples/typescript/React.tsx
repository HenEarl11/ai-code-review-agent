import React, { useEffect, useState } from 'react';

export default function UserDashboard(props) {
  const [users, setUsers] = useState([]);
  const [htmlSnippet, setHtmlSnippet] = useState('');

  useEffect(() => {
    window.addEventListener('resize', () => {
      console.log('resized', window.innerWidth);
    });

    fetchUsers();
  });

  async function fetchUsers() {
    const response = await fetch('/api/users?team=' + props.teamId);
    const data = await response.json();
    console.log('fetched users', data);
    setUsers(data.users);
    setHtmlSnippet(data.bannerHtml);
  }

  return (
    <div>
      <h2>Team Dashboard</h2>
      <div dangerouslySetInnerHTML={{ __html: htmlSnippet }} />
      <ul>
        {users.map((user) => (
          <li>{user.name}</li>
        ))}
      </ul>
    </div>
  );
}
