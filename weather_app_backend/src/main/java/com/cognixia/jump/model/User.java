package com.cognixia.jump.model;

import java.util.List;

import org.springframework.data.annotation.Id;
import org.springframework.data.mongodb.core.mapping.Document;

import jakarta.validation.constraints.Pattern;
import java.util.Objects;

@Document("Users")
public class User {

    @Id
    private String id;

    private String first_name;
    
    private String last_name;

    private String username;

    @Pattern(regexp="^.+@.+$")
    private String email;

    private String profile_image;

    private List<Location> favorites;

    private Location home;

    private String password;


    public User() {
    }

    public User(String id, String first_name, String last_name, String username, String email, String password) {
        this.id = id;
        this.first_name = first_name;
        this.last_name = last_name;
        this.username = username;
        this.email = email;
        this.password = password;
    }

    public User(String id, String first_name, String last_name) {
        this.id = id;
        this.first_name = first_name;
        this.last_name = last_name;
    }

    public User(String id, String first_name, String last_name, String username, String email, String profile_image, List<Location> favorites, Location home, String password) {
        this.id = id;
        this.first_name = first_name;
        this.last_name = last_name;
        this.username = username;
        this.email = email;
        this.profile_image = profile_image;
        this.favorites = favorites;
        this.home = home;
        this.password = password;
    }

    public String getId() {
        return this.id;
    }

    public void setId(String id) {
        this.id = id;
    }

    public String getFirst_name() {
        return this.first_name;
    }

    public void setFirst_name(String first_name) {
        this.first_name = first_name;
    }

    public String getLast_name() {
        return this.last_name;
    }

    public void setLast_name(String last_name) {
        this.last_name = last_name;
    }

    public String getUsername() {
        return this.username;
    }

    public void setUsername(String username) {
        this.username = username;
    }

    public String getEmail() {
        return this.email;
    }

    public void setEmail(String email) {
        this.email = email;
    }

    public String getProfile_image() {
        return this.profile_image;
    }

    public void setProfile_image(String profile_image) {
        this.profile_image = profile_image;
    }

    public List<Location> getFavorites() {
        return this.favorites;
    }

    public void setFavorites(List<Location> favorites) {
        this.favorites = favorites;
    }

    public Location getHome() {
        return this.home;
    }

    public void setHome(Location home) {
        this.home = home;
    }

    public String getPassword() {
        return this.password;
    }

    public void setPassword(String password) {
        this.password = password;
    }

    public User id(String id) {
        setId(id);
        return this;
    }

    public User first_name(String first_name) {
        setFirst_name(first_name);
        return this;
    }

    public User last_name(String last_name) {
        setLast_name(last_name);
        return this;
    }

    public User username(String username) {
        setUsername(username);
        return this;
    }

    public User email(String email) {
        setEmail(email);
        return this;
    }

    public User profile_image(String profile_image) {
        setProfile_image(profile_image);
        return this;
    }

    public User favorites(List<Location> favorites) {
        setFavorites(favorites);
        return this;
    }

    public User home(Location home) {
        setHome(home);
        return this;
    }

    public User password(String password) {
        setPassword(password);
        return this;
    }

    @Override
    public boolean equals(Object o) {
        if (o == this)
            return true;
        if (!(o instanceof User)) {
            return false;
        }
        User user = (User) o;
        return Objects.equals(id, user.id) && Objects.equals(first_name, user.first_name) && Objects.equals(last_name, user.last_name) && Objects.equals(username, user.username) && Objects.equals(email, user.email) && Objects.equals(profile_image, user.profile_image) && Objects.equals(favorites, user.favorites) && Objects.equals(home, user.home) && Objects.equals(password, user.password);
    }

    @Override
    public int hashCode() {
        return Objects.hash(id, first_name, last_name, username, email, profile_image, favorites, home, password);
    }

    @Override
    public String toString() {
        return "{" +
            " id='" + getId() + "'" +
            ", first_name='" + getFirst_name() + "'" +
            ", last_name='" + getLast_name() + "'" +
            ", username='" + getUsername() + "'" +
            ", email='" + getEmail() + "'" +
            ", profile_image='" + getProfile_image() + "'" +
            ", favorites='" + getFavorites() + "'" +
            ", home='" + getHome() + "'" +
            ", password='" + getPassword() + "'" +
            "}";
    }


}
