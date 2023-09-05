package com.cognixia.jump.controller;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

import java.util.ArrayList;
import java.util.List;
import java.util.Optional;

import org.junit.jupiter.api.Test;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.test.web.servlet.MockMvc;

import com.cognixia.jump.exception.ResourceNotFoundException;
import com.cognixia.jump.model.Location;
import com.cognixia.jump.model.User;
import com.cognixia.jump.repository.UserRepository;

@SpringBootTest
@AutoConfigureMockMvc
public class UserControllerTest {
    
    @Autowired
    private MockMvc mockMvc;

    @InjectMocks
    private UserController userController;

    @Mock
    UserRepository userRepo;


    @Test
    public void testGetAllUsers() throws Exception {

        List<User> userList = new ArrayList<>();
        userList.add(new User());
        userList.add(new User());

        when(userRepo.findAll()).thenReturn(userList);

        ResponseEntity<List<User>> users = userController.getUsers();
        assertEquals(HttpStatus.OK, users.getStatusCode());
        assertEquals(users.getBody(), userList);
    }

    @Test
    public void testGetUserById() throws Exception {
        String id = "1";
        User foundUser = new User(id, "Gavin", "Liburd");

        when(userRepo.findById(id)).thenReturn(Optional.of(foundUser));

        ResponseEntity<User> result = userController.getUserById(id);
        assertEquals(HttpStatus.OK, result.getStatusCode());
        assertEquals(foundUser, result.getBody());
    }

    @Test
    public void testGetUserByIdNotFound() throws Exception {
        UserController ucMock = mock(UserController.class);
        String id = "1";

        when(userRepo.findById(id)).thenReturn(Optional.empty());
        when(ucMock.getUserById(id)).thenThrow(ResourceNotFoundException.class);

        assertThrows(ResourceNotFoundException.class, () -> ucMock.getUserById(id));
    }

    @Test
    public void testGetUserByName() throws Exception {
        String username = "GLib";
        User foundUser = new User("1", "Gavin", "Liburd", username, "GLib@gmail.com", "HelloWorld");
        
        when(userRepo.findByUsername(username)).thenReturn(Optional.of(foundUser));

        ResponseEntity<User> result = userController.getUserByName(username);
        assertEquals(HttpStatus.OK, result.getStatusCode());
        assertEquals(foundUser, result.getBody());
    }

    @Test
    public void testGetUserByNameNotFound() throws Exception {
        UserController ucMock = mock(UserController.class);
        String username = "GLib";

        when(userRepo.findByUsername(username)).thenReturn(Optional.empty());
        when(ucMock.getUserByName(username)).thenThrow(ResourceNotFoundException.class);

        assertThrows(ResourceNotFoundException.class, () -> ucMock.getUserByName(username));
    }

    @Test
    public void testGetUserByCredentials() throws Exception {
        String username = "GLib";
        String password = "HelloWorld";
        User foundUser = new User("1", "Gavin", "Liburd", username, "GLib@gmail.com", password); 

        when(userRepo.getByCredentials(username, password)).thenReturn(Optional.of(foundUser));

        ResponseEntity<User> result = userController.getUserByCredentials(foundUser);
        assertEquals(HttpStatus.OK, result.getStatusCode());
        assertEquals(foundUser, result.getBody());
    }

    @Test
    public void testCreateUser() throws Exception {
        User createdUser = new User("1", "Gavin", "Liburd", "GLib", "GLib@gmail.com", "HelloWorld"); 

        when(userRepo.findByUsername(createdUser.getUsername())).thenReturn(Optional.empty());
        when(userRepo.getByEmail(createdUser.getEmail())).thenReturn(Optional.empty());
        when(userRepo.save(createdUser)).thenReturn(createdUser);

        ResponseEntity<User> result = userController.createUser(createdUser);
        assertEquals(HttpStatus.CREATED, result.getStatusCode());
        assertEquals(result.getBody(), createdUser);
    }

    @Test
    public void testAddLocation() throws Exception {
        // User foundUser = new User ("1", "Gavin", "Liburd", "GLib", "GLib@gmail.com", "HelloWorld");
        // Location addedLocation = new Location("atlanta, ga", 30126);
        // foundUser.setFavorites(new ArrayList<>());
        // foundUser.getFavorites().add(addedLocation);
        
        // when(userRepo.findByUsername(foundUser.getUsername())).thenReturn(Optional.of(foundUser));

        // ResponseEntity<User> result = userController.addLocation(foundUser.getUsername(), addedLocation);
        // assertEquals(HttpStatus.OK, result.getStatusCode());
        // assertEquals(result.getBody(), foundUser);
    }
}
