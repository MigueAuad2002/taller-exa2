import { Routes } from '@angular/router';
import { LoginComponent } from './pages/login/login';
import { ListaUsuariosComponent } from './pages/usuarios/lista-usuarios/lista-usuarios';
import { HomeComponent } from './pages/home/home';


export const routes: Routes = [

    { path:'', redirectTo:'login', pathMatch:'full' },
    { path:'login',  component:LoginComponent },
    { path:'home', component: HomeComponent },
    { path:'usuarios', component:ListaUsuariosComponent },
    { path:'**', component:LoginComponent }

];