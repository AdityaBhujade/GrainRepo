import React from 'react';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import CustomerListScreen from '../screens/CustomerListScreen';
import CustomerDetailScreen from '../screens/CustomerDetailScreen';

const Stack = createNativeStackNavigator();

export default function AppNavigator() {
    return (
        <Stack.Navigator
            initialRouteName="CustomerList"
            screenOptions={{
                headerStyle: {
                    backgroundColor: '#111827',
                },
                headerTintColor: '#FFFFFF',
                headerTitleStyle: {
                    fontWeight: '600',
                    fontSize: 17,
                },
                headerShadowVisible: false,
                headerBackTitleVisible: false,
                contentStyle: {
                    backgroundColor: '#F9FAFB',
                },
                animation: 'slide_from_right',
            }}
        >
            <Stack.Screen
                name="CustomerList"
                component={CustomerListScreen}
                options={{ title: 'Grain App' }}
            />
            <Stack.Screen
                name="CustomerDetail"
                component={CustomerDetailScreen}
                options={{ title: 'Customer Details' }}
            />
        </Stack.Navigator>
    );
}
