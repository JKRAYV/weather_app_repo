package com.cognixia.jump.controller;

import java.util.ArrayList;
import java.util.List;
import java.util.Optional;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.mongodb.core.MongoTemplate;
import org.springframework.data.mongodb.core.query.Criteria;
import org.springframework.data.mongodb.core.query.Query;
import org.springframework.data.mongodb.core.query.Update;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PatchMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import com.cognixia.jump.exception.EmptyPropertyException;
import com.cognixia.jump.exception.ResourceNotFoundException;
import com.cognixia.jump.exception.UserExistsException;
import com.cognixia.jump.model.Location;
import com.cognixia.jump.model.User;
import com.cognixia.jump.repository.UserRepository;

import jakarta.validation.Valid;

@RestController
@RequestMapping("/api")
public class UserController {

    @Autowired
    UserRepository userRepo;

    @Autowired
    private MongoTemplate mongoTemplate;

    /********************
	 GET OPERATIONS
	 ********************/

    @GetMapping("/users")
    public ResponseEntity<List<User>> getUsers() {
        
        List<User> users = userRepo.findAll();

        return ResponseEntity.status(200).body(users);
    }
    
    @GetMapping("user/{id}")
    public ResponseEntity<User> getUserById(@PathVariable String id) throws Exception {

        Optional<User> foundUser = userRepo.findById(id);

        if (foundUser.isEmpty()) {
            throw new ResourceNotFoundException("User");
        }
        return ResponseEntity.status(200).body(foundUser.get());
    }

    @GetMapping("user/{username}")
    public ResponseEntity<User> getUserByName(@PathVariable String username) throws Exception {

        Optional<User> foundUser = userRepo.findByUsername(username);

        if (foundUser.isEmpty()) {
            throw new ResourceNotFoundException(username);
        }
        return ResponseEntity.status(200).body(foundUser.get());
    }

    /********************
	 POST OPERATIONS
	 ********************/

    @PostMapping("/user/auth")
    public ResponseEntity<User> getUserByCredentials(@Valid @RequestBody User user) throws Exception {

        Optional<User> validUser = userRepo.getByCredentials(user.getUsername(), user.getPassword());

        if (validUser.isEmpty()) {
            throw new ResourceNotFoundException("User");
        }

        return ResponseEntity.status(200).body(validUser.get());
    }

    @PostMapping("/user")
    public ResponseEntity<User> createUser(@Valid @RequestBody User user) throws Exception {

        if (user.getUsername() == null) 
            throw new EmptyPropertyException("Username");
        
        if (user.getPassword() == null)
            throw new EmptyPropertyException("Password");

        if (user.getFirst_name() == null || user.getLast_name() == null)
            throw new EmptyPropertyException("Name");

        if (user.getEmail() == null)
            throw new EmptyPropertyException("Email");


        Optional<User> existingUser = userRepo.findByUsername(user.getUsername());

        if (existingUser.isPresent()) {
            throw new UserExistsException("User");
        }
        
        user.setFavorites(new ArrayList<>());
        user.setProfile_image("user_bright.png");
        user.setHome(new Location("new york, ny", 10001));

        User created = userRepo.save(user);

        return ResponseEntity.status(201).body(created);
    }

    @PostMapping("/user/location/{username}")
    public ResponseEntity<User> addLocation(@PathVariable String username, @RequestBody Location location) throws Exception {

        Optional<User> foundUser = userRepo.findByUsername(username);

        if (foundUser.isEmpty()) {
            throw new ResourceNotFoundException("User");
        }

        Query query = new Query(Criteria.where("username").is(username));
        Update update = new Update().push("favorites", location);

        mongoTemplate.updateFirst(query, update, User.class);

        Optional<User> updatedUser = userRepo.findByUsername(username);
        return ResponseEntity.status(200).body(updatedUser.get());
    }

    /********************
	 UPDATE OPERATIONS
	 ********************/

    @PatchMapping("/user/{username}")
    public ResponseEntity<User> updateUser(@PathVariable String username, @RequestBody User user) throws Exception {

        Optional<User> foundUser = userRepo.findByUsername(username);

        if (foundUser.isEmpty()) {
            throw new ResourceNotFoundException("User");
        }

        if (user.getUsername() != null) {
            Optional<User> existingUser = userRepo.findByUsername(user.getUsername());

            if (existingUser.isEmpty())
                foundUser.get().setUsername(user.getUsername());
            else
                throw new UserExistsException("User");
        }
        if (user.getFirst_name() != null)
            foundUser.get().setFirst_name(user.getFirst_name());
        if (user.getLast_name() != null)
            foundUser.get().setLast_name(user.getLast_name());
        if (user.getPassword() != null)
            foundUser.get().setPassword(user.getPassword());
        if (user.getEmail() != null)
            foundUser.get().setEmail(user.getEmail());
        if (user.getHome() != null)
            foundUser.get().setHome(user.getHome());
        if (user.getProfile_image() != null)
            foundUser.get().setProfile_image(user.getProfile_image());


        User updatedUser = userRepo.save(foundUser.get());

        return ResponseEntity.status(200).body(updatedUser);
    }

    /********************
	 DELETE OPERATIONS
	 ********************/

     @DeleteMapping("/user/{username}")
     public ResponseEntity<User> deleteUser(@PathVariable String username) throws Exception {

        Optional<User> foundUser = userRepo.findByUsername(username);

        if (foundUser.isEmpty()) {
            throw new ResourceNotFoundException("User");
        }

        userRepo.delete(foundUser.get());

        return ResponseEntity.status(200).body(foundUser.get());
    }

    @DeleteMapping("/user/{username}/{zipCode}")
    public ResponseEntity<User> removeFavorite(@PathVariable String username, @PathVariable Integer zipCode) throws Exception {

        Optional<User> foundUser = userRepo.findByUsername(username);

        if (foundUser.isEmpty()) {
            throw new ResourceNotFoundException("User");
        }

        List<Location> list = foundUser.get().getFavorites();
        Optional<Location> removedFavorite = Optional.empty();

        for (int i = 0; i < list.size(); i++) {

            if (list.get(i).getZip().intValue() == zipCode.intValue()) {
                System.out.println("if succeeded");
                removedFavorite = Optional.of(list.get(i));
                list.remove(i);
            }
        }

        if (removedFavorite.isEmpty()) {
            throw new ResourceNotFoundException("Location");
        }

        User updatedUser = userRepo.save(foundUser.get());

        return ResponseEntity.status(200).body(updatedUser);
    }
}
