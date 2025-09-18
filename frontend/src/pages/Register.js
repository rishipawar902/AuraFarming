/**
 * Modern Registration Page Component for AuraFarming
 * Completely redesigned with better UX and validation
 */

import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { 
  EyeIcon, 
  EyeSlashIcon, 
  UserIcon, 
  PhoneIcon, 
  LockClosedIcon,
  CheckCircleIcon,
  ExclamationCircleIcon
} from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';
import AuthService from '../services/authService';

// InputField component moved outside to prevent re-creation on each render
const InputField = ({ 
  name, 
  type = 'text', 
  placeholder, 
  icon: Icon, 
  showToggle = false,
  showPassword: showPass,
  onTogglePassword,
  value,
  onChange,
  onBlur,
  fieldErrors,
  fieldTouched
}) => {
  const hasError = fieldTouched[name] && fieldErrors[name];
  const hasSuccess = fieldTouched[name] && !fieldErrors[name] && value;

  return (
    <div className="space-y-1">
      <div className="relative">
        <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
          <Icon className={`h-5 w-5 ${
            hasError ? 'text-red-400' : 
            hasSuccess ? 'text-green-400' : 
            'text-gray-400'
          }`} />
        </div>
        
        <input
          id={name}
          name={name}
          type={showToggle ? (showPass ? 'text' : 'password') : type}
          value={value}
          onChange={onChange}
          onBlur={onBlur}
          placeholder={placeholder}
          className={`
            block w-full pl-10 pr-12 py-3 border rounded-lg shadow-sm 
            placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-offset-2
            transition-all duration-200
            ${hasError 
              ? 'border-red-300 focus:border-red-500 focus:ring-red-500' 
              : hasSuccess
              ? 'border-green-300 focus:border-green-500 focus:ring-green-500'
              : 'border-gray-300 focus:border-blue-500 focus:ring-blue-500'
            }
          `}
        />
        
        {showToggle && (
          <button
            type="button"
            onClick={onTogglePassword}
            className="absolute inset-y-0 right-0 pr-3 flex items-center"
          >
            {showPass ? (
              <EyeSlashIcon className="h-5 w-5 text-gray-400 hover:text-gray-600" />
            ) : (
              <EyeIcon className="h-5 w-5 text-gray-400 hover:text-gray-600" />
            )}
          </button>
        )}
        
        {!showToggle && hasSuccess && (
          <div className="absolute inset-y-0 right-0 pr-3 flex items-center">
            <CheckCircleIcon className="h-5 w-5 text-green-400" />
          </div>
        )}
        
        {!showToggle && hasError && (
          <div className="absolute inset-y-0 right-0 pr-3 flex items-center">
            <ExclamationCircleIcon className="h-5 w-5 text-red-400" />
          </div>
        )}
      </div>
      
      {hasError && (
        <p className="text-sm text-red-600 flex items-center">
          <ExclamationCircleIcon className="h-4 w-4 mr-1" />
          {fieldErrors[name]}
        </p>
      )}
      
      {hasSuccess && (
        <p className="text-sm text-green-600 flex items-center">
          <CheckCircleIcon className="h-4 w-4 mr-1" />
          Looks good!
        </p>
      )}
    </div>
  );
};

const Register = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    name: '',
    phoneNumber: '',
    password: '',
    confirmPassword: ''
  });
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [fieldErrors, setFieldErrors] = useState({});
  const [fieldTouched, setFieldTouched] = useState({});

  // Real-time validation
  const validateField = (name, value, currentFormData = formData) => {
    const errors = {};
    
    switch (name) {
      case 'name':
        if (!value.trim()) {
          errors.name = 'Name is required';
        } else if (value.trim().length < 2) {
          errors.name = 'Name must be at least 2 characters';
        } else if (!/^[a-zA-Z\s]+$/.test(value.trim())) {
          errors.name = 'Name can only contain letters and spaces';
        }
        break;
        
      case 'phoneNumber':
        if (!value) {
          errors.phoneNumber = 'Phone number is required';
        } else if (!/^[6-9][0-9]{9}$/.test(value)) {
          errors.phoneNumber = 'Enter a valid 10-digit mobile number';
        }
        break;
        
      case 'password':
        if (!value) {
          errors.password = 'Password is required';
        } else if (value.length < 6) {
          errors.password = 'Password must be at least 6 characters';
        } else if (!/(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/.test(value)) {
          errors.password = 'Password must contain uppercase, lowercase, and number';
        }
        break;
        
      case 'confirmPassword':
        if (!value) {
          errors.confirmPassword = 'Please confirm your password';
        } else if (value !== currentFormData.password) {
          errors.confirmPassword = 'Passwords do not match';
        }
        break;
        
      default:
        break;
    }
    
    return errors;
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    const newFormData = { ...formData, [name]: value };
    setFormData(newFormData);
    
    // Real-time validation with updated form data
    const errors = validateField(name, value, newFormData);
    setFieldErrors(prev => ({ ...prev, [name]: errors[name] }));
    
    // If we're updating password, re-validate confirm password
    if (name === 'password' && formData.confirmPassword) {
      const confirmErrors = validateField('confirmPassword', formData.confirmPassword, newFormData);
      setFieldErrors(prev => ({ ...prev, confirmPassword: confirmErrors.confirmPassword }));
    }
  };

  const handleBlur = (e) => {
    const { name } = e.target;
    setFieldTouched(prev => ({ ...prev, [name]: true }));
  };

  const validateForm = () => {
    const allErrors = {};
    Object.keys(formData).forEach(field => {
      const errors = validateField(field, formData[field], formData);
      if (errors[field]) {
        allErrors[field] = errors[field];
      }
    });
    
    setFieldErrors(allErrors);
    setFieldTouched({
      name: true,
      phoneNumber: true,
      password: true,
      confirmPassword: true
    });
    
    return Object.keys(allErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) {
      toast.error('Please fix the errors below');
      return;
    }

    setIsLoading(true);

    try {
      const registrationData = {
        name: formData.name.trim(),
        phone: formData.phoneNumber,
        password: formData.password,
        language: "en"
      };

      const result = await AuthService.register(registrationData);
      
      if (result.success) {
        toast.success('🎉 Welcome to AuraFarming! Account created successfully!');
        navigate('/dashboard');
      } else {
        toast.error(result.error || 'Registration failed. Please try again.');
      }
    } catch (error) {
      console.error('Registration error:', error);
      toast.error('Something went wrong. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const PasswordStrength = ({ password }) => {
    const checks = {
      length: password.length >= 6,
      uppercase: /[A-Z]/.test(password),
      lowercase: /[a-z]/.test(password),
      number: /\d/.test(password)
    };
    
    const strength = Object.values(checks).filter(Boolean).length;
    const strengthColors = ['bg-red-200', 'bg-yellow-200', 'bg-blue-200', 'bg-green-200'];
    const strengthLabels = ['Weak', 'Fair', 'Good', 'Strong'];

    if (!password) return null;

    return (
      <div className="mt-2">
        <div className="flex space-x-1 mb-2">
          {[0, 1, 2, 3].map((i) => (
            <div
              key={i}
              className={`h-1 flex-1 rounded ${
                i < strength ? strengthColors[strength - 1] : 'bg-gray-200'
              }`}
            />
          ))}
        </div>
        <p className="text-xs text-gray-600">
          Password strength: <span className="font-medium">{strengthLabels[strength - 1] || 'Weak'}</span>
        </p>
        <div className="mt-1 space-y-1">
          {Object.entries({
            'At least 6 characters': checks.length,
            'Uppercase letter': checks.uppercase,
            'Lowercase letter': checks.lowercase,
            'Number': checks.number
          }).map(([requirement, met]) => (
            <div key={requirement} className="flex items-center text-xs">
              <CheckCircleIcon className={`h-3 w-3 mr-1 ${met ? 'text-green-500' : 'text-gray-300'}`} />
              <span className={met ? 'text-green-600' : 'text-gray-400'}>{requirement}</span>
            </div>
          ))}
        </div>
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 via-blue-50 to-indigo-100 flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        {/* Header */}
        <div className="text-center">
          <div className="mx-auto h-16 w-16 bg-gradient-to-r from-green-500 to-blue-600 rounded-full flex items-center justify-center">
            <UserIcon className="h-8 w-8 text-white" />
          </div>
          <h2 className="mt-6 text-3xl font-bold text-gray-900">
            Join AuraFarming
          </h2>
          <p className="mt-2 text-sm text-gray-600">
            Create your account to start smart farming
          </p>
        </div>

        {/* Form */}
        <div className="bg-white rounded-xl shadow-lg p-8 space-y-6">
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Name Field */}
            <InputField
              name="name"
              placeholder="Enter your full name"
              icon={UserIcon}
              value={formData.name}
              onChange={handleInputChange}
              onBlur={handleBlur}
              fieldErrors={fieldErrors}
              fieldTouched={fieldTouched}
            />

            {/* Phone Field */}
            <InputField
              name="phoneNumber"
              type="tel"
              placeholder="Enter your mobile number"
              icon={PhoneIcon}
              value={formData.phoneNumber}
              onChange={handleInputChange}
              onBlur={handleBlur}
              fieldErrors={fieldErrors}
              fieldTouched={fieldTouched}
            />

            {/* Password Field */}
            <div>
              <InputField
                name="password"
                placeholder="Create a strong password"
                icon={LockClosedIcon}
                showToggle={true}
                showPassword={showPassword}
                onTogglePassword={() => setShowPassword(!showPassword)}
                value={formData.password}
                onChange={handleInputChange}
                onBlur={handleBlur}
                fieldErrors={fieldErrors}
                fieldTouched={fieldTouched}
              />
              <PasswordStrength password={formData.password} />
            </div>

            {/* Confirm Password Field */}
            <InputField
              name="confirmPassword"
              placeholder="Confirm your password"
              icon={LockClosedIcon}
              showToggle={true}
              showPassword={showConfirmPassword}
              onTogglePassword={() => setShowConfirmPassword(!showConfirmPassword)}
              value={formData.confirmPassword}
              onChange={handleInputChange}
              onBlur={handleBlur}
              fieldErrors={fieldErrors}
              fieldTouched={fieldTouched}
            />

            {/* Submit Button */}
            <button
              type="submit"
              disabled={isLoading}
              className={`
                group relative w-full flex justify-center py-3 px-4 border border-transparent 
                text-sm font-medium rounded-lg text-white transition-all duration-200
                focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500
                ${isLoading 
                  ? 'bg-gray-400 cursor-not-allowed' 
                  : 'bg-gradient-to-r from-green-500 to-blue-600 hover:from-green-600 hover:to-blue-700 transform hover:scale-105'
                }
              `}
            >
              {isLoading ? (
                <div className="flex items-center">
                  <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Creating Account...
                </div>
              ) : (
                'Create Account'
              )}
            </button>
          </form>

          {/* Divider */}
          <div className="relative">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-gray-300" />
            </div>
            <div className="relative flex justify-center text-sm">
              <span className="px-2 bg-white text-gray-500">Already have an account?</span>
            </div>
          </div>

          {/* Login Link */}
          <div className="text-center">
            <Link 
              to="/login" 
              className="font-medium text-blue-600 hover:text-blue-500 transition-colors duration-200"
            >
              Sign in to your account
            </Link>
          </div>
        </div>

        {/* Features */}
        <div className="bg-white rounded-xl shadow-lg p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Why join AuraFarming?</h3>
          <div className="space-y-3">
            {[
              'AI-powered crop recommendations',
              'Real-time weather insights',
              'Market price tracking',
              'Financial planning tools',
              'Sustainable farming practices'
            ].map((feature, index) => (
              <div key={index} className="flex items-center">
                <CheckCircleIcon className="h-5 w-5 text-green-500 mr-3" />
                <span className="text-sm text-gray-600">{feature}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Register;