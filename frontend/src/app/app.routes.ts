import { Routes } from '@angular/router';
import { LoginComponent } from './pages/login/login';
import { ListaUsuariosComponent } from './pages/usuarios/lista-usuarios/lista-usuarios';
import { HomeComponent } from './pages/home/home';

//LAYOUTS
import { AdminLayoutComponent } from './layouts/admin-layout/admin-layout';

//GUARDS
import { publicGuard } from './guards/public-guard';
import { authGuard } from './guards/auth-guard';


export const routes: Routes = [

    { path:'', redirectTo:'login', pathMatch:'full' },
    { path:'login',  component:LoginComponent, canActivate:[publicGuard] },
    { path:'home', component: HomeComponent, canActivate:[authGuard] },


    //{ path:'usuarios', component:ListaUsuariosComponent, canActivate:[authGuard] },
    //LAYOUT SIDEBAR
    {
        path: '',
        component: AdminLayoutComponent,
        canActivate: [authGuard],
        children: [
        
        { path: 'usuarios', component: ListaUsuariosComponent },
        
        ]
    },
    { path:'**', component:LoginComponent }

];